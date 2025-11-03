def parse_model(model_fp: str) -> dict:
    try:
        nn_model = nnlib.open(model_fp, device=...)  # original parse_model
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

    dto = serialize_model(nn_model)                 # see serializers.py
    elapsed = ...                                   # compute parse duration
    return {"status": "success", "elapsed_ms": elapsed, "model": dto}
