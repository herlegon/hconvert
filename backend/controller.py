from __future__ import annotations
from pprint import pprint
from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from backend.user_preferences import UserPreferences
from ui.main_window import MainWindow


class Controller(QObject):

    def __init__(self, dev: bool):
        super().__init__()
        self.view: MainWindow = None

        self.user_preferences: UserPreferences = UserPreferences()
        self.user_preferences.settings['system']['dev'] = dev


    def exit(self):
        print(f"{__name__}:exit")
        p = self.view.get_user_preferences()
        self.user_preferences.save(p)
        self.view.close()


    def get_user_preferences(self):
        return self.user_preferences.settings


    def save_user_preferences(self, preferences: dict):
        preferences = self.view.get_user_preferences()
        self.user_preferences.save(preferences)


    def set_view(self, view: MainWindow):
        self.view = view
        view.apply_user_preferences(self.user_preferences)
        print("preferences: set_view")
