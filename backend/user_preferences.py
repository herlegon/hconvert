from pprint import pprint
from typing import Any

from PySide6.QtCore import (
    QSettings,
    QObject,
)
from PySide6.QtWidgets import QApplication


class UserPreferences(QObject):

    def __init__(self):
        super().__init__()
        self.tool: str = ["pynnlib", "pynnlib_gui"]

        settings = QSettings(
            QSettings.Format.IniFormat, QSettings.Scope.UserScope, *self.tool
        )

        self._preferences: dict[str, Any] = {
            'window': {},
            'system': {
                'dev': False,
            },
            'user': {},
        }

        # Default geometry
        screens = QApplication.screens()
        screens_count = len(screens)
        screen_width = screens[0].size().width()
        screen_height = screens[0].size().height()

        # (Mandatory) Main window
        if settings.contains("window/screen"):
            self._preferences['window']['screen'] = settings.value("window/screen")
        else:
            self._preferences['window']['screen'] = 0

        self._preferences['window']['geometry'] = [0, 0, screen_width, screen_height]
        try:
            self._preferences['window']['geometry'] = list(
                map(int, settings.value("window/geometry").split(":"))
            )
        except:
            pass

        for group in settings.childGroups():
            if group in ("selection", "window"):
                continue
            settings.beginGroup(group)
            self._preferences[group] = {}
            for k in settings.childKeys():
                v: str = settings.value(k).lower()
                value = True if v == 'true' else False
                self._preferences[group][k] = value
        print("loaded preferences:")
        pprint(self._preferences)



    def save(self, preferences: dict[str, dict[str, Any] | str]):
        print(f"{__name__}.save preferences")
        pprint(preferences)

        settings = QSettings(
            QSettings.Format.IniFormat, QSettings.Scope.UserScope, *self.tool
        )

        # (Mandatory) window
        settings.setValue(
            "window/geometry", ":".join(map(str, preferences['window']['geometry']))
        )
        settings.setValue("window/screen", 0)

        # w = "geometry"
        # if w in preferences:
        #     settings.beginGroup(w)
        #     for name, value in preferences["geometry"].items():
        #         settings.setValue(name, value)

    @property
    def settings(self) -> dict:
        return self._preferences
