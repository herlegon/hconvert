import os
from pathlib import Path
import platform
from pprint import pprint
import sys
from typing import Any

from PySide6.QtCore import (
    QSettings,
    QObject,
)
from PySide6.QtWidgets import QApplication

from backend.path_utils import absolute_path
import tomllib






# class UserPreferences(QObject):

#     def __init__(self):
#         super().__init__()
#         self.tool: str = ["pynnlib", "pynnlib_gui"]

#         settings = QSettings(
#             QSettings.Format.IniFormat, QSettings.Scope.UserScope, *self.tool
#         )

#         self._preferences: dict[str, Any] = {
#             'window': {},
#             'system': {
#                 'dev': False,
#             },
#             'user': {},
#         }

#         # Default geometry
#         screens = QApplication.screens()
#         screens_count = len(screens)
#         screen_width = screens[0].size().width()
#         screen_height = screens[0].size().height()

#         # def _load_defaults(self) -> None:
#         #     screens = QApplication.screens()
#         #     screen_width = screens[0].size().width()
#         #     screen_height = screens[0].size().height()
#         #
#         #     self._preferences["window"].update({
#         #         "screen": 0,
#         #         "geometry": [0, 0, screen_width, screen_height],
#         #     })

#         # (Mandatory) Main window
#         if settings.contains("window/screen"):
#             self._preferences['window']['screen'] = settings.value("window/screen")
#         else:
#             self._preferences['window']['screen'] = 0

#         self._preferences['window']['geometry'] = [0, 0, screen_width, screen_height]
#         try:
#             self._preferences['window']['geometry'] = list(
#                 map(int, settings.value("window/geometry").split(":"))
#             )
#         except:
#             pass

#         for group in settings.childGroups():
#             if group in ("selection", "window"):
#                 continue
#             settings.beginGroup(group)
#             self._preferences[group] = {}
#             for k in settings.childKeys():
#                 v: str = settings.value(k).lower()
#                 value = True if v == 'true' else False
#                 self._preferences[group][k] = value




class UserPreferences:

    def __init__(self, app_name: str = "pynnlib_gui") -> None:
        self.app_name = app_name

        self.app_config_dir = self._platform_config_dir().joinpath("herlegon", self.app_name)
        self.app_config_dir.mkdir(parents=True, exist_ok=True)
        self.app_config_fp: Path = self.app_config_dir.joinpath("user.toml")


        # Initialize default preferences
        self._preferences: dict[str, list | str | int | float | bool | dict] = {
            'window': {
                'screen': 0,
                'geometry': [0, 0, 1920, 1080],  # Default fallback
            },
            'system': {
                'dev': False,
            },
            'user': {},
        }

        if not self.app_config_fp.exists():
            return
        try:
            with self.app_config_fp.open("rb") as f:
                data = tomllib.load(f)
                self._preferences.update(data)
        except Exception as e:
            print(f"Warning: could not read {self.app_config_fp}: {e}")
            with self.app_config_fp.open("rb") as f:
                data = tomllib.load(f)
                self._preferences.update(data)

    def _platform_config_dir(self) -> Path:
        """
        - Windows: %APPDATA%/{org_name}/{app_name}/settings.toml
        - macOS: ~/Library/Application Support/{org_name}/{app_name}/settings.toml
        - Linux: ~/.config/{org_name}/{app_name}/settings.toml
        """
        home = Path.home()
        if sys.platform.startswith("win"):
            base = Path(os.getenv("APPDATA", home.joinpath("AppData", "Roaming")))
        elif sys.platform == "darwin":
            base = home.joinpath("Library", "Application Support")
        else:
            base = Path(os.getenv("XDG_CONFIG_HOME", home.joinpath(".config")))
        return base


    def save(self, preferences: dict[str, list | str | int | float | bool | dict] | None = None) -> None:
        self._preferences = preferences

        lines: list[str] = []
        for section, values in self._preferences.items():
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
                    lines.append(f"{key} = [{', '.join(items)}]")

                elif isinstance(value, bool):
                    lines.append(f"{key} = {'true' if value else 'false'}")

                elif isinstance(value, (int, float)):
                    lines.append(f"{key} = {value}")

                else:
                    lines.append(f'{key} = "{value}"')
            lines.append("")

        try:
            self.app_config_fp.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            print(f"Warning: could not write {self.app_config_fp}: {e}")


    @property
    def settings(self) -> dict[str, Any]:
        return self._preferences

