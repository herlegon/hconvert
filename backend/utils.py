import json
from websockets import (
    ServerConnection,
    ConnectionClosed,
)
from logger import alog


async def send_json(ws: ServerConnection, data: dict):
    """Send JSON safely; ignore if connection is closed."""
    try:
        await ws.send(json.dumps(data))
    except ConnectionClosed:
        alog.debug("send_json: connection closed, skipping send")


