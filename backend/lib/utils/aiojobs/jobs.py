import abc
import asyncio
import concurrent.futures
import random
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


async def _sleep_with_jitter(delay: float, jitter: float) -> None:
    delay += random.uniform(-jitter, jitter)

    if delay < 0:
        return

    await asyncio.sleep(delay)


class RepeatableJob(JobBase):
    def __init__(
        self,
        executor: concurrent.futures.Executor,
        success_delay: float,
        retry_delay: float,
        startup_delay: float,
        startup_jitter: float,
        success_jitter: float,
        retry_jitter: float,
        logger: logging_utils.AbstractLogger,
    ) -> None:
        self._executor = executor

        self._startup_delay = startup_delay
        self._success_delay = success_delay
        self._retry_delay = retry_delay

        self._startup_jitter = startup_jitter
        self._success_jitter = success_jitter
        self._retry_jitter = retry_jitter

        self._logger = logger

        self._finished = False

    async def process(self) -> None:
        await _sleep_with_jitter(self._startup_delay, self._startup_jitter)

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
                    "Job %r has been crashed, it will be retried after %.1f±%.1f seconds",
                    self.name,
                    self._retry_delay,
                    self._retry_jitter,
                )
                if self._finished:
                    self._logger.info("Job %r has been finished", self.name)
                    return
                await _sleep_with_jitter(self._retry_delay, self._retry_jitter)
            else:
                if self._finished:
                    self._logger.info("Job %r has been finished", self.name)
                    return
                self._logger.info(
                    "Job %r finished successfully, it will be repeted after %.1f±%.1f seconds",
                    self.name,
                    self._success_delay,
                    self._success_jitter,
                )
                await _sleep_with_jitter(self._success_delay, self._success_jitter)

    def finish(self) -> None:
        self._finished = True

    @abc.abstractmethod
    def _process(self) -> None: ...


__all__ = [
    "JobProtocol",
    "RepeatableJob",
]
