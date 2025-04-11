pyside6-uic ./ui/designer/ui_main_window.ui -o ./ui/designer/ui_main_window.py
# python ./ui/patch_ui.py --file ./ui/designer/ui_main_window.py

pyside6-uic ./ui/designer/ui_onnx_widget.ui -o ./ui/designer/ui_onnx_widget.py


python pynnlib_gui.py
