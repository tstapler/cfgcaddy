#! /usr/bin/env python
import glob
import logging
import sys
from os.path import basename, exists, expanduser, isdir, isfile, islink, join

from utils import (
    Transaction, create_dirs, create_links,
    find_absences, get_lines_from_file, link_folder,
    parse_regex_file, query_yes_no,
)

logger = logging.getLogger("stapler_linker.linker")

INSTALL_PLATFORM = sys.platform
DEFAULT_DOTFILES_DIR = join(expanduser("~"), "dotfiles")
DEFAULT_HOME_DIR = expanduser("~")

MISSING_FILE_MESSAGE = "Please create a {} file in the same" \
    " directory as the linker python file."


class Linker():

    """Tyler Stapler's Config Linker

    Attributes:
        src: The location of the configuration to be linked
        dest: The location to be copied to
        folder_links: The file containing custom links
        ignore_file: An ignore file for files you want left out
    """

    def __init__(self,
                 src=None,
                 dest=None,
                 customlinks_file=None,
                 ignore_file=None,
                 init_files=False):
        try:
            if not src:
                self.src = DEFAULT_DOTFILES_DIR
            else:
                self.src = src

            if not dest:
                self.dest = DEFAULT_HOME_DIR
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

        except(OSError) as err:
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

        for file in self.customlinks:
            if isdir(file.src):
                if link_folder(file.src, file.dest):
                    modified = True
            if isfile(file.src):
                if create_links([file]):
                    modified = True

        if not modified:
            logger.info("No folders to link")

    def _parse_customlinks(self, filename):
        lines = get_lines_from_file(filename)

        customlinks = []

        for line in lines:
            parts = line.split(":")
            files = glob.glob(join(self.src, parts[0]))
            for file in files:
                fname = basename(file)
                if len(parts) > 1:
                    destination = join(self.dest, parts[len(parts) - 1])

                    if isdir(destination) or len(files) > 1:
                        destination = join(destination, fname)
                else:
                    destination = join(self.dest, fname)

                if not islink(destination):
                    trans = Transaction(join(self.src, file),
                                        join(destination))
                    customlinks.append(trans)

        logger.debug("Custom Links => {}".format(customlinks))
        return customlinks
