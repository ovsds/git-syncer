import asyncio


class TimeoutTimer:
    def __init__(self, timeout: float = 0):
        self._timeout = timeout
        self._deadline = asyncio.get_event_loop().time() + timeout

    @property
    def is_expired(self):
        if self._timeout == 0:
            return False

        return asyncio.get_event_loop().time() > self._deadline


__all__ = [
    "TimeoutTimer",
]
