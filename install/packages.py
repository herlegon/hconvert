python_packages_std = {
    'pip': (),
    'hytils': ("editable"),
    'websockets': (),
    'opencv-python': ('cache'),
    'numpy': (),
    'timm': (),
    'safetensors': (),
    'onnx': (),
    'onnxruntime': (),
    'psutil': (),
    'nvidia-ml-py': (),
    'hsys': ("editable"),
}

# cache
python_packages_add = {
    'cuda': {
        'extra-index-url': "https://download.pytorch.org/whl/cu130",
        'torch': (),
        'torchvision': (),
        'nvidia-cuda-runtime': (),
    },
    'cpu': {
        'extra-index-url': "https://download.pytorch.org/whl/cpu",
        'torch': (),
        'torchvision': (),
    },
    'tensorrt': {
        'extra-index-url': "https://pypi.nvidia.com",
        'tensorrt_cu13_libs': (),
        'tensorrt_cu13_bindings': (),
        'tensorrt_cu13': (),
        'tensorrt': (),
    },
    'directml': {
        'onnxruntime-directml': (),
    },
}

