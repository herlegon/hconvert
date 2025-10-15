# Mandatory
- Get output filepath before converting (*): dummy model like in `convert_to_tensorrt`
- enable/disable widgets depending on arch:
    onnx
    tensorrt

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


# Nice to have

- add optimization level
- change os.path to pathlib  (*)
- dialog to reset history, reload previous model, language (*)
- application icon
- refactor nnlib
- select GPU

(*) reusable
