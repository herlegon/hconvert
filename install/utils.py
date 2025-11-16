from dataclasses import dataclass
import subprocess
import sys
import os
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

@dataclass(slots=True)
class BackendDirectories:
    app: Path
    python_exe: Path
    external: Path
    cache: Path
    models: Path
    rehost: Path | None = None



def get_backend_dirs(
    app_name: str = "herlecon_convert",
    company: str = "herlegon"
) -> BackendDirectories:
    """Get platform-specific backend directory"""

    if sys.platform == "win32":
        # Windows: Use AppData\Local
        base = Path(
            os.environ.get('LOCALAPPDATA', Path.home() / "AppData" / "Local")
        )
        cache_dir = base / company / "cache"
        python_exe = "python.exe"

    elif sys.platform == "linux":
        # Linux: Use XDG Base Directory
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / ".local" / "share"))
        cache_dir = Path(os.environ.get('XDG_DATA_HOME', Path.home() / company / "cache"))
        python_exe = "python"

    elif sys.platform == "darwin":
        # macOS: Use Application Support
        base = Path.home() / "Library" / "Application Support"
        cache_dir = base / company / "cache"
        python_exe = "python"

    else:
        ilog.error()

    return BackendDirectories(
        app=base / company / app_name,
        python_exe=base / company / app_name / "python" / python_exe,
        external=base / company / app_name / "external",
        cache=cache_dir,
        models=base / company / "models",
    )
g_backend_dirs: BackendDirectories = get_backend_dirs()



def get_rehost_dir(company: str = "herlegon") -> Path:
    local_package_dir: Path

    if sys.platform == "win32":
        local_package_dir = Path(os.path.join("A:", company, "rehost"))

    elif sys.platform == "linux":
        local_package_dir = Path(f"/opt/{company}/rehost")

    elif sys.platform == "darwin":
        local_package_dir = Path.home() / company / "rehost"

    return local_package_dir



def get_python_version(python_executable: Path) -> str:
    # Run the python executable with the '-V' or '--version' flag to get the version
    version: str = ""
    try:
        result = subprocess.run(
            [str(python_executable), '--version'],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
    except:
        pass
    return version



def check_site_reachable(url: str, max_retries: int = 3):
    """Check if site is reachable with retries"""
    for attempt in range(max_retries):
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            urlopen(req, timeout=5)
            return True
        except (URLError, HTTPError):
            if attempt < max_retries - 1:
                continue
    return False



