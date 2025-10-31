

ui_dtypes: dict[str, tuple[str, str]] = {
    'fp32': ("fp32", "float32"),
    'fp16': ("fp16", "float16"),
    'bf16': ("bf16", "bfloat16"),
}


ui_shapes: dict[str, tuple[str, str]] = {
    'dynamic': ("dynamic", "Input size is not a constraint"),
    'fixed': ("fixed", "Input image size must be the one specified below"),
    'static': ("static", "Input image size must be the one specified below"),
}


ui_typing: dict[str, tuple[str, str]] = {
    'weak': ("weak", "Legacy. Fallback if conversion is not supported with weak typing."),
    'strong': ("strong", "Preferred"),
}
