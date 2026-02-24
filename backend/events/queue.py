import asyncio
from typing import Optional

_event_queue: Optional[asyncio.Queue] = None


def get_event_queue() -> asyncio.Queue:
    global _event_queue
    if _event_queue is None:
        _event_queue = asyncio.Queue(maxsize=100)
    return _event_queue
