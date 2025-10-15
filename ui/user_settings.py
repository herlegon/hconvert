import os
from pathlib import Path
import sys
import tomllib
from typing import Any
from warnings import warn



class UserSettings:

    def __init__(self, app_name: str = "pynnlib_gui") -> None:

        self.settings_dir: Path = self._platform_config_dir().joinpath("herlegon", app_name)
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.settings_fp: Path = self.settings_dir.joinpath("user_settings.toml")


        # Initialize default preferences
        self._settings: dict[str, list | str | int | float | bool | dict] = {
            'window': {
                'geometry': None,
            },
            'system': {
                'dev': False,
            },
            'user': {},
        }

        if not self.settings_fp.exists():
            return

        try:
            with self.settings_fp.open("rb") as f:
                data = tomllib.load(f)
                self._settings.update(data)

        except Exception as e:
            warn(f"Warning: could not read {self.settings_fp}: {e}")
            with self.settings_fp.open("rb") as f:
                data = tomllib.load(f)
                self._settings.update(data)


    def _platform_config_dir(self) -> Path:
        """
        - Windows: %APPDATA%/{org_name}/{app_name}/settings.toml
        - macOS: ~/Library/Application Support/{org_name}/{app_name}/settings.toml
        - Linux: ~/.config/{org_name}/{app_name}/settings.toml
        """
        home = Path.home()
        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA", home.joinpath("AppData", "Roaming")))
        elif sys.platform == "darwin":
            base = home.joinpath("Library", "Application Support")
        else:
            base = Path(os.getenv("XDG_CONFIG_HOME", home.joinpath(".config")))
        return base


    def save(self, settings: dict[str, list | str | int | float | bool | dict] | None = None) -> None:
        self._settings = settings

        lines: list[str] = []
        for section, values in self._settings.items():
            lines.append(f"[{section}]")
            for key, value in values.items():
                if isinstance(value, list):
                    items = []
                    for v in value:
                        # Convert paths to posix and quote strings
                        if isinstance(v, Path):
                            items.append(f'"{v.as_posix()}"')
                        elif isinstance(v, str):
                            # Detect potential paths with backslash or colon
                            items.append(f'"{v.replace("\\", "/")}"')
                        else:
                            items.append(str(v))
                    string_length: int = sum([len(s) for s in items])
                    if string_length <= 70:
                        lines.append(f"{key} = [{', '.join(items)}]")
                    else:
                        lines.append(f"{key} = [\n  {',\n  '.join(items)}\n]")

                elif isinstance(value, bool):
                    lines.append(f"{key} = {'true' if value else 'false'}")

                elif isinstance(value, (int, float)):
                    lines.append(f"{key} = {value}")

                else:
                    lines.append(f'{key} = "{value}"')
            lines.append("")

        try:
            self.settings_fp.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            print(f"Warning: could not write {self.settings_fp}: {e}")


    @property
    def settings(self) -> dict[str, Any]:
        return self._settings

