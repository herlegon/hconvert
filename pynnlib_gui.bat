pyside6-uic .\ui\designer\main_window.ui -o .\ui\designer\ui_main_window.py
python .\ui\patch_ui.py --file .\ui\designer\ui_main_window.py

python pynnlib_gui.py
