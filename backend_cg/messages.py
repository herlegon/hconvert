from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class WorkerCommand:
    cmd: str                 # "parse", "convert", "cancel", "shutdown"
    payload: Optional[dict] = None

@dataclass
class WorkerEvent:
    type: str                # "progress", "log", "result", "error", "status"
    data: Any = None
