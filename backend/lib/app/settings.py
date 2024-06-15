import os
import re
import warnings

import pydantic
import pydantic_settings

import lib.utils.aiojobs as aiojobs_utils
import lib.utils.git as git_utils
import lib.utils.logging as logging_utils
import lib.utils.pydantic as pydantic_utils


class AppSettings(pydantic_settings.BaseSettings):
    env: str = "production"
    debug: bool = False

    @property
    def is_development(self) -> bool:
        return self.env == "development"

    @property
    def is_debug(self) -> bool:
        if not self.is_development:
            warnings.warn("APP_DEBUG is True in non-development environment", UserWarning)

        return self.debug


class LoggingSettings(pydantic_settings.BaseSettings):
    level: logging_utils.LogLevel = "INFO"
    format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"


class SchedulerSettings(pydantic_settings.BaseSettings):
    one_time: bool = False
    executor_max_workers: int | None = None
    success_delay: int = 5 * 60  # 5 minutes
    retry_delay: int = 1 * 60  # 1 minute
    total_timeout: int = 0  # 10 minutes, 0 means no timeout
    close_timeout: int = 10

    @property
    def aiojobs_scheduler_settings(self) -> aiojobs_utils.Settings:
        return aiojobs_utils.Settings(
            limit=None,
            pending_limit=None,
            close_timeout=self.close_timeout,
        )


class RepoSyncSettings(pydantic_settings.BaseSettings):
    source: pydantic_utils.Expanded[str]
    target: pydantic_utils.Expanded[str]
    include_ref: list[str] = []
    include_ref_regex: list[str] = []
    exclude_ref: list[str] = []
    exclude_ref_regex: list[str] = []

    @property
    def to_dataclass(self) -> git_utils.SyncRepoTask:
        return git_utils.SyncRepoTask(
            source=self.source,
            target=self.target,
            include_ref=set(self.include_ref),
            include_ref_regex=[re.compile(regex) for regex in self.include_ref_regex],
            exclude_ref=set(self.exclude_ref),
            exclude_ref_regex=[re.compile(regex) for regex in self.exclude_ref_regex],
        )


class Settings(pydantic_settings.BaseSettings):
    app: AppSettings = pydantic.Field(default_factory=AppSettings)
    logs: LoggingSettings = pydantic.Field(default_factory=LoggingSettings)
    scheduler: SchedulerSettings = pydantic.Field(default_factory=SchedulerSettings)
    repos: list[RepoSyncSettings] = []

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="GIT_SYNCER_",
        env_nested_delimiter="__",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[pydantic_settings.BaseSettings],
        init_settings: pydantic_settings.PydanticBaseSettingsSource,
        env_settings: pydantic_settings.PydanticBaseSettingsSource,
        dotenv_settings: pydantic_settings.PydanticBaseSettingsSource,
        file_secret_settings: pydantic_settings.PydanticBaseSettingsSource,
    ) -> tuple[pydantic_settings.PydanticBaseSettingsSource, ...]:
        settings_file = os.environ.get("GIT_SYNCER_SETTINGS_YAML", None)
        if settings_file:
            if not os.path.exists(settings_file):
                raise FileNotFoundError(f"Settings file {settings_file} does not exist")

        return (
            env_settings,
            pydantic_settings.YamlConfigSettingsSource(
                settings_cls,
                yaml_file=settings_file,
            ),
        )


__all__ = [
    "AppSettings",
    "LoggingSettings",
    "RepoSyncSettings",
    "Settings",
]
