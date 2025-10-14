- input combobox to repair (pathes)
- keyboard shortcuts
    open: ctrl+o
    tensorrt: t
    onnx: o
    safetensors: s
    start: F10 ? C ?
    save metadata: ctrl+S
    undo metadata: ctrl+Z
- dialog to reset history,
- enable/disable widgets depending on arch
- size constraints ` x `
- show the conversion groupbox corresponding to the activated one (when changing the model)
-safetensors must be deactivated if the input is a safetensors
- if the conversion is not possible, switch to the previous one
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
- is it possible to get the initial size of the onnx info widget to set the left column accordingly? tensorrt ?
- icon buttons
- application icon
- fix: when starting to convert the in model fp is not blocked
- add bf16 for onnx

