pyside6-uic .\ui\designer\ui_main_window.ui -o .\ui\designer\ui_main_window.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_main_window.py
:: python .\ui\patch_ui.py --file .\ui\designer\ui_main_window.py

pyside6-uic .\ui\designer\ui_model_browser_widget.ui -o .\ui\designer\ui_model_browser_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_model_browser_widget.py

pyside6-uic .\ui\designer\ui_pytorch_widget.ui -o .\ui\designer\ui_pytorch_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_pytorch_widget.py

pyside6-uic .\ui\designer\ui_onnx_widget.ui -o .\ui\designer\ui_onnx_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_onnx_widget.py

pyside6-uic .\ui\designer\ui_tensorrt_widget.ui -o .\ui\designer\ui_tensorrt_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_tensorrt_widget.py

pyside6-uic .\ui\designer\ui_metadata_widget.ui -o .\ui\designer\ui_metadata_widget.py
python ./ui/patch_ui.py ./ui/designer/ui_metadata_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_metadata_widget.py

pyside6-uic .\ui\designer\ui_conversion_widget.ui -o .\ui\designer\ui_conversion_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_conversion_widget.py

pyside6-uic .\ui\designer\ui_select_out_dir_widget.ui -o .\ui\designer\ui_select_out_dir_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_select_out_dir_widget.py

pyside6-uic .\ui\designer\ui_onnx_conversion_widget.ui -o .\ui\designer\ui_onnx_conversion_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_onnx_conversion_widget.py

pyside6-uic .\ui\designer\ui_tensorrt_conversion_widget.ui -o .\ui\designer\ui_tensorrt_conversion_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_tensorrt_conversion_widget.py

pyside6-uic .\ui\designer\ui_progress_widget.ui -o .\ui\designer\ui_progress_widget.py
python ..\hwidgets\scripts\q_to_h.py .\ui\designer\ui_progress_widget.py


@REM python pynnlib_gui.py --model A:\ml_models\1x_Anime1080Fixer_SuperUltraCompact.pth
@REM python pynnlib_gui.py --model A:\ml_models\LDVDeNoise_35mm_Compact.pth
@REM python pynnlib_gui.py --model A:\ml_models\1x_Dehalo_Neutral_rplksrs_79k.pth

@REM python pynnlib_gui.py --model A:\ml_models\LDVDeNoise_35mm_Compact_op20_fp16_static_640x480.onnx
@REM python pynnlib_gui.py --model A:\ml_models\LDVDeNoise_35mm_Compact_cc8.9_op20_fp16_static_640x480_10.13.3.9.trtzip
@REM python pynnlib_gui.py --model A:\ml_models\LDVDeNoise_35mm_Compact_op20_fp16.onnx

python pynnlib_gui.py --model A:\ml_models\LDVDeNoise_35mm_Compact_cc8.9_op20_fp16_64x64_768x576_1920x1080_10.13.3.9.trtzip
@REM python pynnlib_gui.py --model A:\ml_models\LDVDeNoise_35mm_Compact.safetensors
@REM python pynnlib_gui.py --model A:\ml_models\LDVDeNoise_35mm_Compact_cc8.9_op20_fp16_fixed_720x540_weak_10.13.3.9.trtzip
