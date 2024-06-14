import asyncio
import concurrent.futures
import logging
import typing

import lib.app.errors as app_errors
import lib.app.settings as app_settings
import lib.git.tasks as git_tasks
import lib.utils.aiojobs as aiojobs_utils
import lib.utils.asyncio as asyncio_utils
import lib.utils.lifecycle_manager as lifecycle_manager_utils
import lib.utils.logging as logging_utils

logger = logging.getLogger(__name__)


class Application:
    def __init__(
        self,
        settings: app_settings.Settings,
        lifecycle_manager: lifecycle_manager_utils.LifecycleManager,
        aiojobs_scheduler: aiojobs_utils.Scheduler,
    ) -> None:
        self._settings = settings
        self._lifecycle_manager = lifecycle_manager
        self._aiojobs_scheduler = aiojobs_scheduler

    @classmethod
    def from_settings(cls, settings: app_settings.Settings) -> typing.Self:
        # Logging

        logging_utils.initialize(
            config=logging_utils.create_config(
                log_level=settings.logs.level,
                log_format=settings.logs.format,
            ),
        )

        logger.info("Initializing application")

        logger.info("Initializing scheduler")
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=settings.scheduler.executor_max_workers)
        aiojobs_scheduler = aiojobs_utils.Scheduler.from_settings(
            settings=settings.scheduler.aiojobs_scheduler_settings
        )

        for repo in settings.repos:
            aiojobs_scheduler.defer_job(
                git_tasks.GitSyncRepoJob(
                    task=repo.to_dataclass,
                    executor=executor,
                    delay_timeout=settings.scheduler.delay_timeout,
                    retry_timeout=settings.scheduler.retry_timeout,
                    one_time=settings.scheduler.one_time,
                )
            )

        logger.info("Initializing lifecycle manager")

        lifecycle_manager = lifecycle_manager_utils.LifecycleManager(logger=logger)
        # Startup
        lifecycle_manager.add_startup_callback(
            callback=lifecycle_manager_utils.StartupCallback(
                callback=aiojobs_scheduler.spawn_deferred_jobs(),
                error_message="Failed to spawn deferred jobs",
                success_message="Deferred jobs have been spawned",
            )
        )
        # Shutdown
        lifecycle_manager.add_shutdown_callback(
            callback=lifecycle_manager_utils.ShutdownCallback.from_disposable_resource(
                name="executor",
                dispose_callback=lambda: executor.shutdown(wait=True),
            )
        )
        lifecycle_manager.add_shutdown_callback(
            callback=lifecycle_manager_utils.ShutdownCallback.from_disposable_resource(
                name="aiojobs_scheduler",
                dispose_callback=aiojobs_scheduler.dispose(),
            )
        )

        logger.info("Creating application")
        application = cls(
            settings=settings,
            lifecycle_manager=lifecycle_manager,
            aiojobs_scheduler=aiojobs_scheduler,
        )

        logger.info("Initializing application finished")

        return application

    async def start(self) -> None:
        try:
            await self._lifecycle_manager.on_startup()
        except lifecycle_manager_utils.LifecycleManager.StartupError as start_error:
            logger.error("Application has failed to start")
            raise app_errors.ServerStartError("Application has failed to start, see logs above") from start_error

        logger.info("Application is starting")
        try:
            await self._start()
        except asyncio.CancelledError:
            logger.info("Application has been interrupted")
        except BaseException as unexpected_error:
            logger.exception("Application runtime error")
            raise app_errors.ServerRuntimeError("Application runtime error") from unexpected_error

    async def _start(self) -> None:
        timer = asyncio_utils.TimeoutTimer(timeout=self._settings.scheduler.timeout)

        while not timer.is_expired:
            if self._aiojobs_scheduler.is_empty:
                logger.info("All jobs have been finished")
                break
            await asyncio.sleep(1)
        else:
            logger.warning("Application has timed out and will be stopped prematurely")
            raise app_errors.ApplicationTimeoutError("Application has timed out")

        logger.info("Application has finished successfully")

    async def dispose(self) -> None:
        logger.info("Application is shutting down...")

        try:
            await self._lifecycle_manager.on_shutdown()
        except lifecycle_manager_utils.LifecycleManager.ShutdownError as dispose_error:
            logger.error("Application has shut down with errors")
            raise app_errors.DisposeError("Application has shut down with errors, see logs above") from dispose_error

        logger.info("Application has successfully shut down")
