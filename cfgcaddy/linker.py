import logging
from os import path
import os
import re
import sys


import inquirer

from cfgcaddy.link import Link
import cfgcaddy.utils as utils

logger = logging.getLogger("cfgcaddy.linker")

INSTALL_PLATFORM = sys.platform


def find_absences(src, dest, ignored_patterns="a^"):
    """ Walk the source directory and return a lists of files and dirs absent
        from the destination directory

    Args:
        source: The path to copy from (Default is the script's location)
        destination The path to copy to (Defaults to home directory)

    Returns:
        absent_files: a list of Links
        absent_dirs: a list of paths to directories
    """
    absent_dirs = []
    absent_files = []
    for root, dirs, files in os.walk(src, topdown=True):
        rel_path = path.relpath(root, src)
        if rel_path == ".":
            rel_path = ""

        # Remove ignored directories from the walk
        dirs[:] = [dir_name for dir_name in dirs
                   if not re.match(ignored_patterns, dir_name)]
        files[:] = [f for f in files
                    if not re.match(ignored_patterns, f)]

        # Create list of dirs that dont exist
        for dir_name in dirs:
            pathname = path.join(dest, rel_path, dir_name)
            if not path.exists(pathname):
                if path.islink(pathname):
                    os.unlink(pathname)  # Fix Broken Links
                absent_dirs.append(pathname)

        # Create a list of files to be symlinked
        for f in files:
            pathname = path.join(dest, rel_path, f)
            if not path.exists(pathname):
                if path.islink(pathname):
                    os.unlink(pathname)  # Fix Broken Links
                # Add the source and destination for the symlink
                absent_files.append(Link(path.join(root, f),
                                    pathname))

    return absent_files, absent_dirs


class Linker():

    """Tyler Stapler's Config Linker
    """

    def __init__(self, linker_config,
                 prompt=True):

        if not linker_config:
            raise Exception("Linker requires Config!")

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
            find_absences(self.config.linker_src,
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
