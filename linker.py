#! /usr/bin/env python
from collections import namedtuple
from os.path import exists, join, relpath, expanduser, split
from os import walk, symlink, makedirs
from filecmp import dircmp
from shutil import move
import os
import sys
import re

from utils import (create_dirs, create_links, get_lines_from_file,
                   parse_regex_file, query_yes_no, sync_dir)

INSTALL_PLATFORM = sys.platform
CONFIG_DIR = split(os.path.abspath(__file__))[0] + "/.."
HOME_DIR = expanduser("~")
MISSING_FILE_MESSAGE = "Please create a {} file in the same" \
                       " directory as the linker python file."

Link = namedtuple('Link', ['src', 'dest'])


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
                self.folder_links_file = join(CONFIG_DIR, ".folderlinks")
                exists(self.folder_links_file)
            except IOError:
                print(MISSING_FILE_MESSAGE.format(".folderlinks"))
                sys.exit(1)
        if ignore_file is None:
            try:
                self.ignore_file = join(CONFIG_DIR, ".linkerignore")
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

        absent_files, absent_dirs = self.find_absences()

        if len(absent_files) == 0:
            print("No files to move")
            return

        print("Preparing to symlink the following files")
        print("\n".join(link.dest for link in absent_files))
        if query_yes_no("Are these the correct files?"):
            create_dirs(dirs=absent_dirs)
            create_links(links=absent_files)

    def find_absences(self):
        """ Walk the source directory and return a lists of diles and dirs absent
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
        for root, dirs, files in walk(self.src, topdown=True):
            rel_path = relpath(root, self.src)
            if rel_path == ".":
                rel_path = ""

            # Remove ignored directories from the walk
            dirs[:] = [dir_name for dir_name in dirs
                       if not re.match(self.ignored_patterns, dir_name)]
            files[:] = [f for f in files
                        if not re.match(self.ignored_patterns, f)]

            # Create list of dirs that dont exist
            for dir_name in dirs:
                if not exists(join(self.dest, rel_path, dir_name)):
                    absent_dirs.append(join(self.dest, rel_path, dir_name))

            # Create a list of files to be symlinked
            for f in files:
                if not exists(join(self.dest, rel_path, f)):
                    # Add the source and destination for the symlink
                    absent_files.append(Link(join(root, f),
                                        join(self.dest, rel_path, f)))

        return absent_files, absent_dirs

    def link_folders(self):
        """Link all the files in the folder link file

        Args:
            None

        Returns:
            None
        """

        for folder in self.folder_patterns:
            dest_folder_path = join(self.dest, folder)
            src_folder_path = join(self.src, folder)

            if exists(dest_folder_path) and exists(src_folder_path):
                # Syncronize dirs
                print(dest_folder_path)
                print(src_folder_path)
                dcmp = dircmp(dest_folder_path, src_folder_path)
                print dcmp.left_only
                # print dcmp.report_full_closure()
                print dcmp.subdirs
            elif exists(dest_folder_path) and not exists(src_folder_path):
                print("Moving and symlinking {}" % folder)
                # move(dest_folder_path, src_folder_path)
                # symlink(src_folder_path, dest_folder_path)
            elif not exists(dest_folder_path) and exists(src_folder_path):
                print("Symlinking {}" % folder)
                # symlink(src_folder_path, dest_folder_path)


if __name__ == '__main__':
    linker = Linker()

    linker.link_configs()
    linker.link_folders()
