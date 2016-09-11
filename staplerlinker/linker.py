#! /usr/bin/env python
from os.path import exists, join, expanduser
import logging
import sys

from utils import (create_dirs, create_links, get_lines_from_file,
                   parse_regex_file, query_yes_no, find_absences, link_folder)

logger = logging.getLogger("stapler_linker.linker")

INSTALL_PLATFORM = sys.platform
CONFIG_DIR = join(expanduser("~"), "dotfiles")
HOME_DIR = expanduser("~")

MISSING_FILE_MESSAGE = "Please create a {} file in the same" \
                       " directory as the linker python file."


class Linker(object):
    """Tyler Stapler's Config Linker

    Attributes:
        src: The location of the configuration to be linked
        dest: The location to be copied to
        folder_links:
        ignore_file:
    """
    def __init__(self,
                 src=None,
                 dest=None,
                 customlinks_file=None,
                 ignore_file=None):
        try:
            if not src:
                self.src = CONFIG_DIR
            else:
                self.src = src

            if not dest:
                self.dest = HOME_DIR
            else:
                self.dest = dest

            if not customlinks_file:
                    self.customlinks_file = join(self.src, ".customlinks")
            else:
                self.customlinks_file = customlinks_file
            if not ignore_file:
                    self.ignore_file = join(self.src, ".linkerignore")
            else:
                self.ignore_file = ignore_file

            exists(self.src)
            exists(self.dest)
            exists(self.customlinks_file)
            exists(self.ignore_file)

        except OSError, err:
                logger.error(MISSING_FILE_MESSAGE.format(err.file))
                sys.exit(1)

        self.customlinks = self._parse_customlinks(self.customlinks_file)
        self.ignored_patterns = parse_regex_file(self.ignore_file)

    def link_configs(self):
        """Symlinks configuration files to the destination directory

        Parses the ignore file for regexes and then generates a list of files
        which need to be simulinked"""

        absent_files, absent_dirs = find_absences(self.src, self.dest,
                                                  self.ignored_patterns)

        if len(absent_files) == 0:
            logger.info("No files to move")
            return

        logger.info("Preparing to symlink the following files")
        print("\n".join(link.dest for link in absent_files))
        if query_yes_no("Are these the correct files?"):
            create_dirs(dirs=absent_dirs)
            create_links(links=absent_files)

    def create_custom_links(self):
        """Link all the files in the customlink file

        Args:
            None

        Returns:
            None
        """
        modified = False

        for src, dest in self.customlinks:
            modified = modified or link_folder(src, dest)

        if not modified:
            logger.info("No folders to link")

    def _parse_customlinks(self, filename):
        lines = get_lines_from_file(filename)

        customlinks = []

        for line in lines:
            parts = line.split(":")
            if len(parts) > 1:
                for i in range(1, len(parts)):
                    customlinks.append([join(self.src, parts[0]),
                                        join(self.dest, parts[i])])
            else:
                customlinks.append([join(self.src, parts[0]),
                                    join(self.dest, parts[0])])

        return customlinks
