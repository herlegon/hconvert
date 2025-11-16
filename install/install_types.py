from dataclasses import dataclass
from pathlib import Path
import requests

PLATFORMS: tuple[str] = ('win32', 'linux', 'darwin')

# an external package is a program/helper
# that will be installed in the external directory
@dataclass
class ExtPackage:
    name: str
    filename: str
    key: str

    # Installation, skip is not necessary except for dev and to keep the
    # definitions in the config file
    skip: bool
    install_dir: Path = None
    installed: bool = False

    # Where to download from
    tag: Path = None
    size: int = 0
    host: str = ''
    response: requests.Response | None = None

    # Downloaded/cached
    downloaded: bool = False
    cache_file: Path = None
    do_cache: bool = False

    def __post_init__(self):
        self.skip = bool(self.filename == '')
