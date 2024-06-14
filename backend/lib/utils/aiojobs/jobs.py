import abc
import asyncio
import concurrent.futures
import typing

import lib.utils.logging as logging_utils


class JobProtocol(typing.Protocol):
    @property
    def name(self) -> str: ...

    async def process(self) -> None: ...


class JobBase(abc.ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    async def process(self) -> None: ...


class RepeatableJob(JobBase):
    def __init__(
        self,
        executor: concurrent.futures.Executor,
        delay_timeout: float,
        retry_timeout: float,
        logger: logging_utils.AbstractLogger,
    ) -> None:
        self._executor = executor
        self._delay_timeout = delay_timeout
        self._retry_timeout = retry_timeout
        self._logger = logger

        self._finished = False

    async def process(self) -> None:
        while True:
            loop = asyncio.get_running_loop()
            try:
                await loop.run_in_executor(
                    executor=self._executor,
                    func=self._process,
                )
            except asyncio.CancelledError:
                self._logger.info("Job %r has been cancelled", self.name)
                return
            except Exception:
                self._logger.exception(
                    "Job %r has been crashed, it will be retried after %.1f seconds",
                    self.name,
                    self._retry_timeout,
                )
                if self._finished:
                    self._logger.info("Job %r has been finished", self.name)
                    return
                await asyncio.sleep(self._retry_timeout)
            else:
                if self._finished:
                    self._logger.info("Job %r has been finished", self.name)
                    return
                self._logger.info(
                    "Job %r finished successfully, it will be repeted after %.1f seconds",
                    self.name,
                    self._delay_timeout,
                )
                await asyncio.sleep(self._delay_timeout)

    def finish(self) -> None:
        self._finished = True

    @abc.abstractmethod
    def _process(self) -> None: ...


__all__ = [
    "JobProtocol",
    "RepeatableJob",
]
