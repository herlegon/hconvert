from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEventLoop
import sys

from .utils import get_backend_directory

def run_installer_and_wait(
        logo_path=None,
        local_packages_dir: Path = None,
    ):

    from .install_window import InstallationWindow
    from .first_time_dialog import FirstTimeSetupDialog
    backend_dir = get_backend_directory()
    if local_packages_dir and local_packages_dir.exists():
        backend_dir['_local_packages'] = local_packages_dir

    # Check if this is the first time installation
    is_first_time = not backend_dir['app'].exists()

    # First-time dialog
    keep_installers = False
    if is_first_time:
        dialog = FirstTimeSetupDialog()
        keep_installers = dialog.get_choice()

    # Create installer window
    installer = InstallationWindow(
        backend_dirs=backend_dir,
        logo_path=logo_path,
        keep_installers=keep_installers
    )

    installer.show()
    installer.start_installation()

    # Block here until installation_window closes
    loop = QEventLoop()
    installer.destroyed.connect(loop.quit)
    loop.exec()

    return True  # or return relevant info
