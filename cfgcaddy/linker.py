import logging
import sys
from os import path

import inquirer

import utils

logger = logging.getLogger("cfgcaddy.linker")

INSTALL_PLATFORM = sys.platform


class Linker():

    """Tyler Stapler's Config Linker
    """

    def __init__(self, linker_config,
                 prompt=True):

        self.config = linker_config
        self.prompt = prompt

        self.custom_links = self.config.links
        self.ignored_patterns = self.config.ignore_patterns

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
        if not self.prompt or inquirer.prompt([
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
                if utils.link_folder(file.src, file.dest, self.prompt):
                    modified = True
            if path.isfile(file.src):
                if utils.create_links([file]):
                    modified = True

        if not modified:
            logger.info("No folders to link")
