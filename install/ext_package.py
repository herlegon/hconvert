from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
from pprint import pprint
import signal
import sys
import tomllib
from typing import Any
import requests
import shutil
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
import tempfile
from hytils import (
    get_extension,
    lightcyan,
    lightgreen,
    red,
    reformat_datetime,
)
from load_package_config import create_ext_packages, load_packages_toml_
from utils import g_backend_dirs, get_rehost_dir
from logger import ilog
from urllib.error import URLError, HTTPError
from install_types import ExtPackage


def clean_cache(package: ExtPackage) -> None:
    # clean cache of other version
    ilog.debug(f"Remove old cache")
    for file in package.cache_file.parent.iterdir():
        if (
            file.is_file()
            and file.name.startswith(package.key)
            and file.name not in (
                package.tag,
                package.filename
            )
        ):
            file.unlink()

    if not package.do_cache:
        ilog.debug(f"Remove cached installed files")
        for file in package.cache_file.parent.iterdir():
            if file.is_file() and file.name.startswith(package.key):
                file.unlink()



def download_package_from_host(
    package: ExtPackage,
    retry: int = 3,
    progress: Progress| None = None,
    task_id: TaskID | None = None,
) -> bool:

    if not package.tag:
        ilog.error(f"Tag file not valid for package: {package.name}")
        return False

    tmp_dir = package.cache_file.parent
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tag_file = (tmp_dir / package.tag)
    if tag_file.exists():
        tag_file.unlink()

    ilog.debug(f"Download package: {package.filename}")

    _retry: int = retry
    while _retry:
        ilog.debug(f"Downloading: {package.name} to {tmp_dir}")
        if progress is not None:
            progress.update(task_id, total=package.size)
            progress.start_task(task_id)

        with open(package.cache_file, "wb") as f:
            try:
                for data in package.response.iter_content(chunk_size=1024):
                    f.write(data)
                    if progress is not None:
                        progress.update(task_id, advance=len(data))
            except Exception as e:
                ilog.debug("[W] Retry download, error: type(e)")
                _retry -= 1
                continue

        if _retry == 0:
            ilog.debug(f"[E] failed downloading {package.filename}")
            return False

        _retry = 0

    tag_file.touch()
    return True


def install_ext_package(package: ExtPackage) -> bool:
    ilog.debug(f"Install: {package.name}")
    install_dir = package.install_dir

    extension: str = get_extension(str(package.cache_file))
    if install_dir.exists():
        shutil.rmtree(install_dir)

    if extension == '.zip':
        import zipfile
        with zipfile.ZipFile(package.cache_file, "r") as f:
            f.extractall(install_dir)

    else:
        install_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(package.cache_file, install_dir)

    (install_dir / package.tag).touch()
    package.installed = True

    ilog.debug(f"{package.name} installed in {install_dir}")

    return True



def download_package_(
    package: ExtPackage,
    progress: Progress | None = None,
    retry: int = 3,
    use_local_host: bool = False,
    reinstall: bool = False,
) -> ExtPackage:
    last_modified: str = ""
    downloadable: bool = False
    if use_local_host:
        local_host = g_backend_dirs.local_host
        if local_host and local_host.is_dir():
            # Use local rehost for testing purpose
            local_rehost_fp: Path = local_host / package.filename
            if local_rehost_fp.is_file():
                dt = datetime.fromtimestamp(local_rehost_fp.stat().st_mtime)
                formatted_time = dt.strftime("%Y-%m-%dT%H-%M-%S")
                last_modified = formatted_time
                ilog.debug(f"use local rehost: {package.name}, {last_modified}")
                package.size = local_rehost_fp.stat().st_size
            else:
                ilog.warning(f"Asked to use local host, but file {local_rehost_fp} not found")
        else:
            ilog.warning(f"Asked to use local host ({local_host}) but directory doesn't exist")

    else:
        # Get info from host and update package info
        url: str = f"{package.host}/{package.filename}"
        ilog.debug(f"url: {url}")

        for attempt in range(retry):
            response: requests.Response
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

            except (URLError, HTTPError):
                ilog.warning(f"Host not reachable")
                if attempt < retry - 1:
                    continue

            except requests.exceptions.RequestException as e:
                if str(e).startswith('404'):
                    ilog.error(f"{package.filename} not found on the host")
                    break
                else:
                    ilog.error(f"Exception while fetching: {str(e)}")
                if attempt < retry - 1:
                    continue

            downloadable = True
            last_modified: str = reformat_datetime(response.headers['Last-Modified'])
            package.size = int(response.headers.get('Content-length', 0))
            package.response = response

    package.tag = (
        f"{package.filename}_{last_modified}"
        if last_modified
        else ""
    )
    if package.do_cache:
        package.cache_file = g_backend_dirs.cache / package.filename
    else:
        package.cache_file = Path(tempfile.gettempdir()) / "herlegon" / package.filename
    ilog.debug(f"package: {'\n'.join(str(package).split(','))}")

    # Check if installed: use a timestamp file for this
    if package.tag:
        tag_fp: Path = package.install_dir / package.tag
        if tag_fp.exists():
            package.installed = True
            ilog.debug(f"{package.name} already installed")

            # Remove cache if installed
            if not package.do_cache and not reinstall:
                try:
                    package.cache_file.unlink()
                except:
                    pass
                tag_fp.unlink()

            if not reinstall:
                clean_cache(package=package)
                return package
        else:
            ilog.debug(f"{package.name} not installed yet")
    else:
        ilog.warning(f"{package.name} not tag found ({package.tag})")

    package.installed = False

    # Detect if cached
    ilog.debug(f"Searching cache file: {package.cache_file}")
    tag_fp: Path = g_backend_dirs.cache / package.tag
    if (
        package.tag and tag_fp.exists()
        and package.cache_file.is_file()
        and package.cache_file.stat().st_size == package.size
    ):
        package.downloaded = True
        ilog.debug(f"{package.name} Use cached installer")

    # Use local host to simulate a download
    if (
        not package.downloaded
        and use_local_host
        and g_backend_dirs.local_host
    ):
        local_fp: Path = g_backend_dirs.local_host / package.filename
        ilog.debug(f"Searching {local_fp}")
        if local_fp.exists():
            cache_dir = package.cache_file.parent
            cache_dir.mkdir(parents=True, exist_ok=True)
            ilog.debug(f"Copy from local host: {local_fp} -> {cache_dir}")
            shutil.copy(local_fp, cache_dir)
            (cache_dir / package.tag).touch(exist_ok=True)
            package.downloaded = True

    # Finally download it from host
    if not package.downloaded and downloadable:
        package.downloaded = download_package_from_host(
            package,
            progress=progress,
            task_id=progress.add_task(
                "[green] Installing...",
                name=package.name,
                start=False
            ),
            retry=retry
        )

    return package


def dl_and_install_ext_package(
    package: ExtPackage,
    progress: Progress | None = None,
    retry: int = 3,
    use_local_host: bool = False,
    reinstall: bool = False,
) -> bool:
    if package.skip:
        return True
    ilog.info(f"{package.name}")
    package = download_package_(
        package,
        progress=progress,
        retry=retry,
        use_local_host=use_local_host,
        reinstall=reinstall,
    )

    # Install package
    if not package.installed or reinstall:
        if package.downloaded:
            installed: bool = install_ext_package(package)
            if installed:
                clean_cache(package=package)
            package.installed = installed

    if package.installed:
        ilog.info(f"{package.name}: installed")
    else:
        ilog.error(f"{package.name}: Failed to install")

    return package.installed



def download_install_ext_packages(
    packages: tuple[ExtPackage],
    retry: int = 3,
    threads: int = 1,
    reinstall: bool = False,
    use_local_host: bool = False,
) -> bool:
    threads = min(max(threads, 1), len(packages))
    progress = Progress(
        TextColumn("[bold cyan]{task.fields[name]}", justify="right"),
        BarColumn(bar_width=40),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )

    packages = [package for package in packages if not package.skip]
    if threads == 1:
        with progress:
            for package in packages:
                success = dl_and_install_ext_package(
                    package=package,
                    progress=progress,
                    retry=retry,
                    use_local_host=use_local_host,
                    reinstall=reinstall,
                )
                if not success:
                    return False
    else:
        success: bool = True
        with progress:
            with ThreadPoolExecutor(max_workers=threads) as executor:
                for result in executor.map(
                    lambda args: dl_and_install_ext_package(**args),
                    [
                        {
                            'package': package,
                            'progress': progress,
                            'retry': retry,
                            'use_local_host': use_local_host,
                            'reinstall': reinstall
                        }
                        for package in packages
                    ]
                ):
                    success = success and result
        return success

    return True




if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    import sys
    from logger import ilog
    ilog.setLevel("DEBUG")

    with open(Path("packages.toml"), "rb") as f:
        data: dict[str, Any] = tomllib.load(f)

    packages_cfg = load_packages_toml_(data)
    pprint(packages_cfg)

    external_packages = create_ext_packages(
        packages_cfg, external_dir=g_backend_dirs.external
    )
    print(lightcyan(" ".join (("-" * 40, sys.platform, "-" * 40))))
    pprint(external_packages)
    print()

    python_package = create_ext_packages(
        packages_cfg,
        external_dir=g_backend_dirs.python_exe.parent.parent,
        section='python'
    )
    print(lightcyan(" ".join (("-" * 40, "python", "-" * 40))))
    pprint(python_package)
    print()

    g_backend_dirs.local_host = get_rehost_dir()
    print(lightcyan(" ".join (("-" * 40, "backend directories", "-" * 40))))
    pprint(g_backend_dirs)


    if python_package:
        installed: bool = download_install_ext_packages(
            packages=python_package,
            reinstall=True,
            threads=1,
            use_local_host=True
        )
        if installed:
            print(lightgreen("All packages installed"))
        else:
            print(red("Error: missing package(s)"))
    else:
        print(lightgreen("No packages to install"))


    if external_packages:
        installed: bool = download_install_ext_packages(
            packages=external_packages,
            reinstall=True,
            threads=1,
            use_local_host=True
        )
        if installed:
            print(lightgreen("All packages installed"))
        else:
            print(red("Error: missing package(s)"))
    else:
        print(lightgreen("No packages to install"))

