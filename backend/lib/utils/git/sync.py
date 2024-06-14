import dataclasses
import re
import tempfile

import git

import lib.utils.logging as logging_utils

DESTINATION_REMOTE_NAME = "destination"


@dataclasses.dataclass
class SyncRepoTask:
    source: str
    target: str
    include_ref: set[str]
    include_ref_regex: list[re.Pattern[str]]
    exclude_ref: set[str]
    exclude_ref_regex: list[re.Pattern[str]]


def _is_ref_included(
    ref_path: str,
    task: SyncRepoTask,
):
    if ref_path in task.exclude_ref:
        return False

    for regex in task.exclude_ref_regex:
        if regex.match(ref_path):
            return False

    if ref_path in task.include_ref:
        return True

    for regex in task.include_ref_regex:
        if regex.match(ref_path):
            return True

    if not task.include_ref and not task.include_ref_regex:
        return True

    return False


def sync_repo(task: SyncRepoTask, logger: logging_utils.AbstractLogger):
    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info("Cloning from %s to %s", task.source, task.target)
        temp_repo = git.Repo.clone_from(task.source, temp_dir, mirror=True)

        logger.info("Fetched refs:")
        for ref in temp_repo.references:
            logger.info("\t%s", ref.path)

        logger.info("Deleting excluded refs...")
        for ref in temp_repo.references:
            if _is_ref_included(ref_path=ref.path, task=task):
                continue

            logger.info("\t%s", ref.path)
            git.Reference.delete(temp_repo, ref.path)

        logger.info("Creating destination remote...")
        temp_repo.create_remote(DESTINATION_REMOTE_NAME, url=task.target)

        logger.info("Pushing...")
        destination = temp_repo.remote(name=DESTINATION_REMOTE_NAME)
        push_info = destination.push(mirror=True)

        logger.info("Pushed refs:")
        for info in push_info:
            logger.info("\t%s %s", info.remote_ref_string, info.summary.strip("\n"))

        push_info.raise_if_error()


__all__ = [
    "SyncRepoTask",
    "sync_repo",
]
