import asyncio
import psutil
from websockets import (
    ServerConnection,
    ConnectionClosedOK,
    ConnectionClosedError,


)
from hutils import red, yellow
from utils import send_json
from logger import alog

TELEMETRY_RATE: float = 1.5


def get_system_usage() -> dict:
    ram = psutil.virtual_memory().used / (1024**2)
    cpu = psutil.cpu_percent(interval=None)
    data = {"type": "system_usage", "cpu": cpu, "ram": ram, "vram": 0}
    return data


async def telemetry_loop(ws: ServerConnection):
    try:
        while True:
            data = get_system_usage()
            await send_json(ws, data)
            await asyncio.sleep(TELEMETRY_RATE)

    except ConnectionClosedOK:
        alog.info("Telemetry loop: client disconnected normally")

    except ConnectionClosedError as e:
        alog.warning(f"Telemetry loop: connection closed with error: {e}")

    except asyncio.CancelledError:
        alog.info("Telemetry loop cancelled")

    except Exception as e:
        alog.exception(f"Telemetry loop crashed: {e}")


