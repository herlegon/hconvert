import sys
import os
from pathlib import Path
from typing import Literal


def get_backend_directory(
    app_name: str = "herlecon_convert",
    company: str = "herlegon"
) -> dict[Literal['app', 'cache', 'models', '_local_packages'], Path]:
    """Get platform-specific backend directory"""

    if sys.platform == "win32":
        # Windows: Use AppData\Local
        base = Path(
            os.environ.get('LOCALAPPDATA', Path.home() / "AppData" / "Local")
        )
        cache_dir = base / company_dir / "cache"
        local_packages_dir = Path(os.path.join("A:", company, "install"))

    elif sys.platform == "darwin":
        # macOS: Use Application Support
        base = Path.home() / "Library" / "Application Support"
        cache_dir = base / company_dir / "cache"
        local_packages_dir = Path.home() / company / "install"

    elif sys.platform == "linux":
        # Linux: Use XDG Base Directory
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / ".local" / "share"))
        cache_dir = Path(os.environ.get('XDG_DATA_HOME', Path.home() / company / "cache"))
        local_packages_dir = Path(f"/opt/{company}/install")

    return {
        'app': base / company / app_name,
        'cache': cache_dir,
        'models': base / company / "models",
        # For debug
        '_local_packages': local_packages_dir
    }






