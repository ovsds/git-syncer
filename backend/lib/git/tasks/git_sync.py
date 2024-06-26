import concurrent.futures
import logging
import typing

import lib.utils.aiojobs as aiojobs_utils
import lib.utils.git as git_utils
import lib.utils.logging as logging_utils


class GitSyncRepoJob(aiojobs_utils.RepeatableJob):
    _count: typing.ClassVar[int] = 0

    def __init__(
        self,
        task: git_utils.SyncRepoTask,
        executor: concurrent.futures.Executor,
        startup_delay: float,
        success_delay: float,
        retry_delay: float,
        startup_jitter: float,
        success_jitter: float,
        retry_jitter: float,
        one_time: bool = False,
    ):
        self._task = task
        self._one_time = one_time
        self._id = self._generate_id()

        super().__init__(
            executor=executor,
            startup_delay=startup_delay,
            success_delay=success_delay,
            retry_delay=retry_delay,
            startup_jitter=startup_jitter,
            success_jitter=success_jitter,
            retry_jitter=retry_jitter,
            logger=logging_utils.PrefixAdapter(
                prefix=f"GitSyncRepoJob[{self._id}] ",
                logger=logging.getLogger(__name__),
            ),
        )

    def _generate_id(self) -> int:
        self.__class__._count += 1
        return self.__class__._count

    @property
    def name(self) -> str:
        return f"{super().name}[id={self._id}]"

    def _process(self) -> None:
        try:
            git_utils.sync_repo(
                task=self._task,
                logger=self._logger,
            )
        finally:
            if self._one_time:
                self._logger.info("Job is set to one-time mode, finishing...")
                self.finish()


__all__ = [
    "GitSyncRepoJob",
]
