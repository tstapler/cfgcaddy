import glob
import logging
import sys
from os import path

import inquirer

import utils
from link import Link

logger = logging.getLogger("cfgcaddy.linker")

INSTALL_PLATFORM = sys.platform


class Linker():

    """Tyler Stapler's Config Linker
    """

    def __init__(self, linker_config):

        self.config = linker_config

        self.custom_links = self.link_object_factory(self.config.links)
        self.ignored_patterns = utils.join_ignore_regex(self.config.ignore)

    def create_links(self):
        """Symlinks configuration files to the destination directory

        Parses the ignore file for regexes and then generates a list of files
        which need to be simulinked"""

        # TODO: Rewrite find_absences
        absent_files, absent_dirs = \
            utils.find_absences(self.config.linker_src,
                                self.config.linker_dest,
                                self.ignored_patterns)

        if len(absent_files) == 0:
            logger.info("No files to move")
            return

        logger.info("Preparing to symlink the following files")
        print("\n".join(link.dest for link in absent_files))
        if inquirer.prompt([
            inquirer.Confirm("correct", "Are these the correct files?")
        ]).get("correct"):
            utils.create_dirs(dirs=absent_dirs)
            utils.create_links(links=absent_files)

    def create_custom_links(self):
        """Link all the files in the customlink file

        Args:
            None

        Returns:
            None
            """
        modified = False

        for file in self.custom_links:
            if path.isdir(file.src):
                if utils.link_folder(file.src, file.dest):
                    modified = True
            if path.isfile(file.src):
                if utils.create_links([file]):
                    modified = True

        if not modified:
            logger.info("No folders to link")

    def link_object_factory(self, patterns):
        custom_links = []

        for line in patterns:
            parts = line.split(":")
            files = glob.glob(path.join(self.config.linker_src, parts[0]))
            for file in files:
                fname = path.basename(file)
                if len(parts) > 1:
                    destination = path.join(
                        self.config.linker_dest, parts[len(parts) - 1])

                    if path.isdir(destination) or len(files) > 1:
                        destination = path.join(destination, fname)
                else:
                    destination = path.join(self.config.linker_dest, fname)

                if not path.islink(destination):
                    trans = Link(
                        path.join(self.config.linker_src, file),
                                  path.join(destination))
                    custom_links.append(trans)

        logger.debug("Custom Links => {}".format(custom_links))
        return custom_links
