
- enable/disable widgets depending on arch

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

- icon buttons
- when the conversion is stuck -> move conversion to another thread or create a separate python script?...


Nice to have

- change os.path to pathlib
- dialog to reset history
- application icon
