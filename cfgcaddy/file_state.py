import logging
from enum import Enum
from pathlib import Path
from typing import Union

from cfgcaddy.utils import convert_to_path

logger = logging.getLogger()


class FileState(str, Enum):
    MISSING = "MISSING"
    LINK = "LINK"
    BROKEN_LINK = "BROKEN_LINK"
    LINK_FILE = "LINK_FILE"
    LINK_DIRECTORY = "LINK_DIRECTORY"
    DIRECTORY = "DIRECTORY"
    FILE = "FILE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_pathlike(cls, f: Union[str, Path]):
        f = convert_to_path(f)
        if f.is_symlink():
            if f.is_file():
                return FileState.LINK_FILE
            elif f.is_dir():
                return FileState.LINK_DIRECTORY
            elif not f.exists():
                return FileState.BROKEN_LINK
        elif not f.exists():
            return FileState.MISSING
        elif f.is_file():
            return FileState.FILE
        elif f.is_dir():
            return FileState.DIRECTORY
        logger.error(f"Encountered a file in unknown state: {f}")
        return FileState.UNKNOWN
