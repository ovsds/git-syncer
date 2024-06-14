import logging
import typing


class PrefixAdapter(logging.LoggerAdapter[logging.Logger]):
    def __init__(self, prefix: str, logger: logging.Logger) -> None:
        super().__init__(logger, {})
        self._prefix = prefix

    def process(
        self,
        msg: str,
        kwargs: typing.MutableMapping[str, typing.Any],
    ) -> tuple[str, typing.MutableMapping[str, typing.Any]]:
        return f"{self._prefix}{msg}", kwargs


__all__ = [
    "PrefixAdapter",
]
