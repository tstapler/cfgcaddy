from __future__ import annotations
import logging
import os
from os import path
from pathlib import Path
from typing import Union, Optional, List

from questionary import prompt

logger = logging.getLogger()

Pathlike = Union[str, Path]


def user_confirm(question: str, default: bool = True) -> bool:
    """Ask the user to confirm a choice

    Args:
        question (string): a string that is presented to the user.
        default (string): the answer if the user just hits <Enter>.
            It must be True, False or None (meaning
            an answer is required of the user).

    Returns "answer" return value is True for "yes" or False for "no".
    """
    return prompt(
        [{"type": "confirm", "name": "ok", "message": question, "default": default}]
    ).get("ok", False)


def make_parent_dirs(file_path: Pathlike) -> None:
    try:
        os.makedirs(path.dirname(file_path))
    except OSError as e:  # Python >2.5
        pass


def expand_path(file_path: Pathlike) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(file_path)))


def create_dirs(dirs: Optional[List[str]] = None) -> None:
    """Creates all folders in dirs

    Args:
        dirs ([string]): A list of paths to be linked

    Returns:
        None: Does not return anything
    """
    if dirs:
        for dir_name in dirs:
            try:
                os.makedirs(dir_name)
            except OSError:
                logger.error("Unable to create directory: {}", dir_name)


def convert_to_path(f: Union[str, Path]) -> Path:
    if isinstance(f, str):
        f = Path(f)
    return f
