#! /usr/bin/env python
from os.path import exists, join, expanduser, split, islink
from os import symlink, rmdir, remove
from filecmp import dircmp
from shutil import move, make_archive, rmtree
import os
import sys

from utils import (create_dirs, create_links, move_files, get_lines_from_file,
                   parse_regex_file, query_yes_no, find_absences)

INSTALL_PLATFORM = sys.platform
CONFIG_DIR = join(split(os.path.abspath(__file__))[0], "..")
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
                 src=CONFIG_DIR,
                 dest=HOME_DIR,
                 folder_links_file=None,
                 ignore_file=None):
        self.src = src
        self.dest = dest

        if folder_links_file is None:
            try:
                self.folder_links_file = join(self.src, ".folderlinks")
                exists(self.folder_links_file)
            except IOError:
                print(MISSING_FILE_MESSAGE.format(".folderlinks"))
                sys.exit(1)
        if ignore_file is None:
            try:
                self.ignore_file = join(self.src, ".linkerignore")
                exists(self.ignore_file)
            except IOError:
                print(MISSING_FILE_MESSAGE.format(".linkerignore"))
                sys.exit(1)

        self.folder_patterns = get_lines_from_file(self.folder_links_file)
        self.ignored_patterns = parse_regex_file(self.ignore_file)

    def link_configs(self):
        """Symlinks configuration files to the destination directory

        Parses the ignore file for regexes and then generates a list of files
        which need to be simulinked"""

        absent_files, absent_dirs = find_absences(self.src, self.dest,
                                                  self.ignored_patterns)

        if len(absent_files) == 0:
            print("No files to move")
            return

        print("Preparing to symlink the following files")
        print("\n".join(link.dest for link in absent_files))
        if query_yes_no("Are these the correct files?"):
            create_dirs(dirs=absent_dirs)
            create_links(links=absent_files)

    def link_folders(self):
        """Link all the files in the folderlink file

        Args:
            None

        Returns:
            None
        """

        for folder in self.folder_patterns:
            dest_folder_path = join(self.dest, folder)
            src_folder_path = join(self.src, folder)

            if (exists(dest_folder_path) and
                exists(src_folder_path) and not
                    islink(dest_folder_path)):

                # Syncronize dirs
                absent_files, absent_dirs = find_absences(dest_folder_path,
                                                          src_folder_path)
                print make_archive("{}_backup".format(folder).strip("."),
                                   "zip", root_dir=dest_folder_path)
                create_dirs(absent_dirs)
                move_files(absent_files)
                rmtree(dest_folder_path)
                symlink(src_folder_path, dest_folder_path)

            elif exists(dest_folder_path) and not exists(src_folder_path):
                print("Moving and symlinking {}".format(folder))
                print make_archive("{}_backup".format(folder).strip("."),
                                   "zip", root_dir=dest_folder_path)
                move(dest_folder_path, src_folder_path)
                rmtree(dest_folder_path)
                symlink(src_folder_path, dest_folder_path)

            elif not exists(dest_folder_path) and exists(src_folder_path):
                print("Symlinking {}".format(folder))
                symlink(src_folder_path, dest_folder_path)


if __name__ == '__main__':
    linker = Linker()

    linker.link_folders()
    linker.link_configs()
