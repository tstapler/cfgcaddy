import os

from cfgcaddy import LINK_MODE


class Link():
    def __init__(self, src, dest):
        """docstring for __init__"""

        self.src = src
        self.dest = dest

        if not os.path.exists(src):
            raise Exception("The source directory needs to exist!")

    def __repr__(self):
        return "{} => {}".format(self.src, self.dest)

    def execute(self, mode=LINK_MODE.SKIP):

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

        # TODO: if dest doesnt exist
        pass
