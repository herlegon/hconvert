from copy import deepcopy
from pprint import pprint
import tomllib
from pathlib import Path
from typing import Any
from ext_package import ExtPackage


from pathlib import Path
from dataclasses import dataclass
import tomllib
import sys

from hytils import lightcyan, lightgreen, red, yellow

import sys
from pathlib import Path
from dataclasses import dataclass
import requests
from utils import g_backend_dirs

PLATFORMS: tuple[str] = ('win32', 'linux', 'darwin')

@dataclass
class ExtPackage:
    name: str
    filename: str

    # Installation, skip is not necessary except for dev and to keep the
    # definitions in the config file
    skip: bool
    install_dir: Path = None
    installed: bool = False

    # Where to download from
    last_modified: str = ''
    size: int = 0
    host: str = ''
    response: requests.Response | None = None

    # Downloaded/cached
    downloaded: bool = False
    cache_file: Path = None
    do_cache: bool = False

    def __post_init__(self):
        self.skip = bool(self.filename == '')



def load_packages_toml_(data: dict[str, Any]) -> dict[str, Any]:
    """
    Load TOML [platforms], capturing all keys as defaults and merging platform-specific packages.
    """
    for k_section in data.keys():
        section: dict[str, Any] = data[k_section]

        # Separate default configs from platform-specific configs
        default_config = {}
        platform_config = {}
        to_remove = []
        for key, value in section.items():
            if key in PLATFORMS:
                platform_config[key] = value
            else:
                default_config[key] = value
                to_remove.append(key)
        for k in to_remove:
            del section[k]

        # Merge defaults with each platform-specific config
        for platform in PLATFORMS:
            # Create a new section for undefined platform
            if platform not in platform_config.keys():
                platform_config[platform] = {}

            # Merge default keys
            platform_default = deepcopy(default_config)
            to_remove = []
            for k, v in platform_config[platform].items():
                if not isinstance(v, dict):
                    platform_default.update({k: v})
                    to_remove.append(k)
            for k in to_remove:
                del platform_config[platform][k]

            # Append the consolidated default section
            platform_config[platform]['default'] = platform_default

        data[k_section] = platform_config

    return data





def create_ext_packages(
    packages_cfg: dict,
    external_dir: Path,
    platform: str = None
) -> list[ExtPackage]:
    """
    Convert platforms dict to list of ExtPackage for the current platform.

    Args:
        packages_cfg: The processed configuration dict
        external_dir: Base directory for external packages
        platform: Platform name (defaults to sys.platform)

    Returns:
        List of ExtPackage objects
    """
    # Automatically select the current platform if not specified
    #  used for validation
    if platform is None:
        platform = sys.platform

    # External packages
    ext_packages_cfg: dict = packages_cfg['external']

    # Get the platform-specific config
    platform_config: dict[str, Any] = ext_packages_cfg.get(platform, {})
    default_config: dict[str, Any] = platform_config.get('default', {})

    packages: list[ExtPackage] = []
    for key, value in platform_config.items():
        # Skip if it's a simple value or the default section
        if not isinstance(value, dict) or key == 'default':
            continue

        # Check if this looks like a package definition (has filename or is explicitly configured)
        if 'filename' in value:
            skip = value.get('skip', False)
            # print(red(f"{key}: skip={skip}"))
            if not skip:
                package_name = value.get('name', default_config.get(f"{key}_name", key))

                packages.append(
                    ExtPackage(
                        name=package_name,
                        install_dir=external_dir / key,
                        filename=value.get('filename', ''),
                        host=value.get('host', ''),
                        do_cache=value.get('do_cache', False),
                        skip=value.get('skip', False),
                    )
                )

    for p in packages:
        for k in ('host', 'do_cache'):
            # keys are accessibles because it's a dataclass with slots=False
            if k in p.__dict__ and not p.__dict__[k]:
                instance = p.__dict__[k]
                p.__dict__[k] = default_config.get(
                    k,
                    False if isinstance(instance, bool)
                    else "" if isinstance(instance, str)
                    else None
                )

    return packages




if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    with open(Path("packages.toml"), "rb") as f:
        data: dict[str, Any] = tomllib.load(f)

    packages_cfg = load_packages_toml_(data)

    print(lightgreen(" ".join(("-" * 40, "config", "-" * 40))))
    pprint(packages_cfg)

    external_dir = g_backend_dirs.external

    if True:
        for platform_key in PLATFORMS:
            print(lightcyan(" ".join (("-" * 40, platform_key, "-" * 40))))
            packages = create_ext_packages(
                packages_cfg,
                external_dir=external_dir,
                platform=platform_key
            )
            pprint(packages)
            print()

    else:
        print(lightcyan(" ".join (("-" * 40, sys.platform, "-" * 40))))
        packages = create_ext_packages(
            packages_cfg,
            external_dir=external_dir,
        )
        pprint(packages)
        print()
