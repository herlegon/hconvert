(*) reusable


# Mandatory
- Add opt level because it may change the basename: do not add it for level = 3 (default)
- when an onnx model is loaded, if model.torch_arch is none "no support for this"
- when a model is not supported, open dialog for message and clear all widgets
- when an exception, show it as the same way as unsupported

- Try to keep the previous conversion selection,
    if the conversion is not possible, switch to the previous one
        if cuda:
            safetensors: tensorrt, onnx
            pth: tensorrt, onnx, safetensors
            onnx: tensorrt
            tensorrt: nothing
        if not cuda:
            safetensors: onnx
            pth: onnx, safetensors
            onnx: nothing
            tensorrt: cannot load
- button's icons (*)
- when the conversion is stuck -> move conversion to another thread or create a separate python script?...
- validate shapes (onnx, tensorrt): minimum size and size ordering
- save user settings on important event but not resize:
    * when model has been sucessfully loaded
    * save current model/out_dir/selection when starting a conversion (option)
- Installation (*)
- System capabilities (*)
- log file and textplainedit (*)
- copy from combobox and model lineedit doesn't work
- disable paste in model browser

# Nice to have

- add tensorrt optimization level
- select GPU (*)
- refactor nnlib (*)
- change os.path to pathlib  (*)
- dialog to reset history, reload previous model, language (*)
- application icon

# To verify
- Get output filepath before converting (*): remaining to do: ONNX->TENSORT
