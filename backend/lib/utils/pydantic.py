import os
import re
import typing

import pydantic

import lib.utils.logging as logging_utils

T = typing.TypeVar("T")


def expand_envs(value: str) -> str:
    def env_repl(match: re.Match[str]) -> str:
        env_key = match.group(1)
        env_value = os.environ[env_key]

        return env_value

    return re.sub(r"{{env \"([A-Z_]+)\"}}", env_repl, value)


def expand_secret_envs(value: str) -> str:
    def env_repl(match: re.Match[str]) -> str:
        env_key = match.group(1)
        env_value = os.environ[env_key]

        logging_utils.register_secret(env_value, f'{{{{env "{env_key}"}}}}')

        return env_value

    return re.sub(r"{{secret_env \"([A-Z_]+)\"}}", env_repl, value)


Expanded = typing.Annotated[
    T,
    pydantic.BeforeValidator(expand_envs),
    pydantic.BeforeValidator(expand_secret_envs),
]

__all__ = ["Expanded"]
