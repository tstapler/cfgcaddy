import logging
import os

from cfgcaddy import LINK_MODE
from cfgcaddy.utils import make_parent_dirs

logger = logging.getLogger("cfgcaddy.link")


class Link():
    def __init__(self, src, dest):
        """docstring for __init__"""

        self.src = src
        self.dest = dest

        if not os.path.exists(src):
            raise Exception("The source directory needs to exist!")

    def __repr__(self):
        return "{} => {}".format(self.src, self.dest)

    @property
    def is_linked(self):
        return os.path.islink(self.dest)

    def create(self, mode=LINK_MODE.SKIP):
        if os.path.exists(self.dest):
            pass
        # TODO: if dest exists
        # TODO: if dest is a link
        # TODO: If override
        # TODO: If skip

        # TODO: if dest is a file
        # TODO: If override
        # TODO: If skip

        # TODO: if dest is a folder

        # TODO: if src is a folder
        # TODO: If override
        # TODO: If skip
        # TODO: if src is a file
        # TODO: If override
        # TODO: If skip
        else:
            # if dest doesnt exist create it
            try:
                make_parent_dirs(self.dest)
                os.symlink(self.src, self.dest)
            except (OSError) as err:
                logger.error("Can't make link from {} to {} because {}".format(
                    self.src, self.dest, err.strerror))
