pyside6-uic ./ui/designer/ui_main_window.ui -o ./ui/designer/ui_main_window.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_main_window.py

pyside6-uic ./ui/designer/ui_model_browser_widget.ui -o ./ui/designer/ui_model_browser_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_model_browser_widget.py

pyside6-uic ./ui/designer/ui_pytorch_widget.ui -o ./ui/designer/ui_pytorch_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_pytorch_widget.py

pyside6-uic ./ui/designer/ui_onnx_widget.ui -o ./ui/designer/ui_onnx_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_onnx_widget.py

pyside6-uic ./ui/designer/ui_tensorrt_widget.ui -o ./ui/designer/ui_tensorrt_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_tensorrt_widget.py

pyside6-uic ./ui/designer/ui_metadata_widget.ui -o ./ui/designer/ui_metadata_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_metadata_widget.py

pyside6-uic ./ui/designer/ui_conversion_widget.ui -o ./ui/designer/ui_conversion_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_conversion_widget.py

pyside6-uic ./ui/designer/ui_select_out_dir_widget.ui -o ./ui/designer/ui_select_out_dir_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_select_out_dir_widget.py

pyside6-uic ./ui/designer/ui_onnx_conversion_widget.ui -o ./ui/designer/ui_onnx_conversion_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_onnx_conversion_widget.py

pyside6-uic ./ui/designer/ui_tensorrt_conversion_widget.ui -o ./ui/designer/ui_tensorrt_conversion_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_tensorrt_conversion_widget.py

pyside6-uic ./ui/designer/ui_progress_widget.ui -o ./ui/designer/ui_progress_widget.py
python ../hwidgets/scripts/q_to_h.py ./ui/designer/ui_progress_widget.py


export QT_QPA_PLATFORM=xcb
python pynnlib_gui.py --model /home/adg/z-personnel/ml_models/1x-HurrDeblur-SuperUltraCompact_metadata.pth
# python pynnlib_gui.py --model /home/adg/z-personnel/ml_models/1x_Anime1080Fixer_SuperUltraCompact_op20_fp32None.onnx

