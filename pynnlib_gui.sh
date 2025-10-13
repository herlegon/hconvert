pyside6-uic ./ui/designer/ui_main_window.ui -o ./ui/designer/ui_main_window.py
# python ./ui/patch_ui.py --file ./ui/designer/ui_main_window.py

pyside6-uic ./ui/designer/ui_model_browser_widget.ui -o ./ui/designer/ui_model_browser_widget.py

pyside6-uic ./ui/designer/ui_pytorch_widget.ui -o ./ui/designer/ui_pytorch_widget.py
pyside6-uic ./ui/designer/ui_onnx_widget.ui -o ./ui/designer/ui_onnx_widget.py
pyside6-uic ./ui/designer/ui_tensorrt_widget.ui -o ./ui/designer/ui_tensorrt_widget.py

pyside6-uic ./ui/designer/ui_metadata_widget.ui -o ./ui/designer/ui_metadata_widget.py

pyside6-uic ./ui/designer/ui_conversion_widget.ui -o ./ui/designer/ui_conversion_widget.py
pyside6-uic ./ui/designer/ui_select_out_dir_widget.ui -o ./ui/designer/ui_select_out_dir_widget.py
pyside6-uic ./ui/designer/ui_onnx_conversion_widget.ui -o ./ui/designer/ui_onnx_conversion_widget.py
pyside6-uic ./ui/designer/ui_tensorrt_conversion_widget.ui -o ./ui/designer/ui_tensorrt_conversion_widget.py

export QT_QPA_PLATFORM=xcb
python pynnlib_gui.py --model /home/adg/z-personnel/ml_models/1x-HurrDeblur-SuperUltraCompact_metadata.pth

