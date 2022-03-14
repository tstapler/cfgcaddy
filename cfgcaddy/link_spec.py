from enum import Flag
from pathlib import Path
from typing import Protocol


class LinkingResult(Flag):
    """The result from a linking operation"""

    SKIPPED = False
    CREATED = True
    FAILED = False


class LinkSpec(Protocol):
    src: Path
    dest: Path

    def __repr__(self) -> str:
        return "{} => {}".format(self.src, self.dest)

    def create(self, interactive: bool = False) -> LinkingResult:
        pass
