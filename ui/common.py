import os
from hutils import parent_directory, absolute_path
from typing import Literal

from PySide6.QtCore import (
    Qt,
)
from PySide6.QtGui import (
    QPixmap,
    QImage,
    QColor,
    QPainter,
)
# from PySide6.QtWidgets import (

# )


DEFAULT_SIZE: tuple[int, int] = (720, 540)

PREDEFINED_SIZE: dict[str, tuple[int, int]] = {
    "480p 16:9 (DVD)": (854, 480),
    "480p 4:3": (640, 480),
    "480p NTSC": (720, 480),
    "540p NTSC 4:3 sq": (720, 540),
    "576p 4:3 sq": (768, 576),
    "720p 4:3": (960, 720),
    "720p (HD ready)": (1280, 720),
    "1080p (Full HD)": (1920, 1080),
    "2160p (4K UHDTV)": (3840, 2160)
}

predefined_shapes_inv: dict[str, str] = {
    "x".join(map(str, v)): k for k, v in PREDEFINED_SIZE.items()
}

ShapeStrategyName = Literal['static', 'dynamic', 'fixed']


ONNX_DEFAULT_SETTINGS: dict[str, str | bool | int | tuple[int, int]] = {
    'version': 21,
    'dtype': 'fp32',
    'shape_strategy': 'static',
    'shape': (720, 540),
}


TENSORRT_DEFAULT_SETTINGS: dict[str, str | bool | int | tuple[int, int]] = {
    'version': 21,
    'dtype': 'fp16',
    'shape_strategy': 'fixed',
    'shape_min':(64,64),
    'shape_opt': (720, 540),
    'shape_max': (1920, 1080),
}




SUPPORTED_MODEL_EXTENSIONS: tuple[str] = (
    ".engine",
    ".trtzip",
    ".onnx",
    ".pt",
    ".pth",
    ".safetensors",
    ".param",
    ".ncnn",
)


ICON_DIR = absolute_path(os.path.join(parent_directory(__file__), "icons"))
def load_png_scaled(filename: str, height: int) -> QPixmap:
    """
    Load a PNG image from `path` and scale it to the given height
    while keeping its aspect ratio.

    Args:
        path (str): Path to the PNG file.
        height (int): Desired height in pixels.

    Returns:
        QPixmap: The scaled QPixmap.
    """
    pixmap_fp = os.path.join(ICON_DIR, filename)
    pixmap = QPixmap(pixmap_fp)

    if pixmap.isNull():
        raise FileNotFoundError(f"Cannot load image: {pixmap_fp}")
    if height != -1 and height != pixmap.height():
        return pixmap.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)

    return pixmap
