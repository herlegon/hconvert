from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import os
from pathlib import Path
from pprint import pprint
import signal
import sys
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

from hytils import (
    get_extension,
    lightgreen,
    lightgrey,
    red,
    reformat_datetime,
)
from utils import g_backend_dirs
from logger import ilog
from urllib.error import URLError, HTTPError


# an external package is a program/helper
# that will be installed in the external directory
@dataclass
class ExtPackage:
    name: str
    dirname: Path
    filename: str
    size: int = 0
    host: str = ''
    response: requests.Response | None = None
    last_modified: str = ''
    downloaded: bool = False
    installed: bool = False
    install_dir: Path = None
    cache_file: Path = None
    skip: bool = False
    do_cache: bool = False

    def __post_init__(self):
        self.skip = bool(self.filename == '')



def download_package(
    package: ExtPackage,
    retry: int = 3,
    progress: Progress| None = None,
    task_id: TaskID | None = None,
) -> bool:
    tmp_dir: str = os.path.dirname(package.cache_file)
    os.makedirs(tmp_dir, exist_ok=True)

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
                ilog.info("[W] Retry download, error: type(e)")
                _retry -= 1
                continue

        if _retry == 0:
            ilog.info(f"[E] failed downloading {package.filename}")
            return False

        _retry = 0

    if package.last_modified:
        open(os.path.join(tmp_dir, package.last_modified), 'w').close()

    return  True



def install_ext_package(package: ExtPackage) -> bool:
    ilog.info(lightgrey(f"  install"))
    install_dir: str = package.install_dir

    extension: str = get_extension(package.cache_file)
    if os.path.exists(install_dir):
        shutil.rmtree(install_dir)

    if extension == '.zip':
        import zipfile
        with zipfile.ZipFile(package.cache_file, "r") as f:
            f.extractall(install_dir)

    else:
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
        os.makedirs(install_dir)
        shutil.move(package.cache_file, install_dir)

    package.installed = True
    open(os.path.join(install_dir, package.last_modified), 'w').close()
    if not package.do_cache:
        try:
            shutil.rmtree(os.path.dirname(package.cache_file))
        except:
            pass
    ilog.info(lightgrey(f"  {package.name} installed"))

    return True



def dl_and_install_ext_package(
    package: ExtPackage,
    progress: Progress | None = None,
    retry: int = 3,
    use_local_rehost: bool = False,
    reinstall: bool = False,
) -> bool:
    if package.skip:
        return True
    ilog.info(f"Package: {package.name}")

    last_modified: str = ""
    if use_local_rehost and g_backend_dirs.rehost:
        # Use local rehost for testing purpose
        local_rehost = g_backend_dirs.rehost
        local_rehost_fp: Path = local_rehost / package.filename
        if local_rehost_fp.is_file():
            last_modified = local_rehost.stat().st_mtime

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
                    ilog.error(f"{package.filename} not found")
                else:
                    ilog.error(f"Exception while fetching: {str(e)}")
                if attempt < retry - 1:
                    continue

            last_modified: str = reformat_datetime(response.headers['Last-Modified'])
            package.size = int(response.headers.get('Content-length', 0))
            package.response = response

    package.last_modified = last_modified
    package.cache_file = g_backend_dirs.cache / package.filename
    ilog.error(f"Cache file: {package.cache_file}")

    # Check if installed: use a timestamp file for this
    if last_modified:
        package.install_dir = g_backend_dirs.external / package.dirname
        timestamp_fp: Path = package.install_dir / last_modified
        if timestamp_fp.exists():
            package.installed = True
            ilog.info(lightgrey(f"  already installed"))
            try:
                shutil.rmtree(package.cache_file.parent)
            except:
                pass
            if not reinstall:
                return True

    package.installed = False

    # Detect if cached
    cache_last_modified: Path = g_backend_dirs.cache / package.dirname / last_modified
    if (
        cache_last_modified.exists()
        and package.cache_file.is_file()
        and package.cache_file.stat().st_size == package.size
    ):
        package.downloaded = True
        ilog.info(lightgrey(f"  {cache_last_modified} already downloaded"))

    # Use local rehost
    if not package.downloaded and use_local_rehost and g_backend_dirs.rehost:
        local_fp = g_backend_dirs.cache / package.filename
        if local_fp.exists():
            ilog.info(f"Using local rehost: {local_fp}")
            package.downloaded = True

    # Finally download it from host
    if not package.downloaded:
        package.downloaded = download_package(
            package,
            progress=progress,
            task_id=progress.add_task(
                "[green] Installing...",
                name=package.name,
                start=False
            ),
            retry=retry
        )

    if not package.downloaded:
        return False

    # Install package
    return install_ext_package(package)




def download_install_ext_packages(
    packages: tuple[ExtPackage],
    rehost_url: str,
    retry: int = 3,
    threads: int = 1,
    reinstall: bool = False,
    use_local_rehost: bool = False,
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

    for package in packages:
        package.host = rehost_url

    packages = [package for package in packages if not package.skip]
    if threads == 1:
        with progress:
            for package in packages:
                success = dl_and_install_ext_package(
                    package=package,
                    progress=progress,
                    retry=retry,
                    use_local_rehost=use_local_rehost,
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
                            'use_local_rehost': use_local_rehost,
                            'reinstall': reinstall
                        }
                        for package in packages
                    ]
                ):
                    success = success and result
        return success

    return True



def external_packages() -> tuple[ExtPackage]:
    packages: tuple[ExtPackage] = (
        ExtPackage(
            name="FFmpeg",
            dirname='ffmpeg',
            filename=(
                "ffmpeg_win32_x64.zip"
                if sys.platform == "win32"
                else "ffmpeg_linux_amd64.zip"
            ),
            do_cache=True,
        ),
        ExtPackage(
            name="VS python",
            dirname="vspython",
            filename=(
                "vspython.zip"
                if sys.platform == "win32"
                else ""
            ),
            do_cache=True,
        ),
    )
    return packages


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    import logging
    import sys
    from logger import ilog
    ilog.addHandler(logging.StreamHandler(sys.stdout))
    ilog.setLevel("DEBUG")

    rehost_url: str = "https://github.com/JepEtau/external_rehost/releases/download/external"

    installed: bool = download_install_ext_packages(
        external_packages(), rehost_url=rehost_url, threads=1,
    )
    if installed:
        print(lightgreen("All packages installed"))
    else:
        print(red("Error: missing package(s)"))

    installed: bool = download_install_ext_packages(
        external_packages(), rehost_url=rehost_url, threads=1, reinstall=True,
    )
    if installed:
        print(lightgreen("All packages installed"))
    else:
        print(red("Error: missing package(s)"))
