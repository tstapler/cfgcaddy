import distutils
import logging
import os
import shutil
from distutils import dir_util
from os import path

import pathspec

import cfgcaddy
import cfgcaddy.utils as utils
from cfgcaddy.link import Link

logger = logging.getLogger("cfgcaddy.linker")


def find_absences(src, dest, ignored_patterns=[]):
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

    default_ignore = ["!.*", cfgcaddy.DEFAULT_CONFIG_NAME, ".git"]

    ignored = pathspec.PathSpec.from_lines('gitwildmatch',
                                           ignored_patterns + default_ignore)

    for root, dirs, files in os.walk(src, topdown=True):
        rel_path = path.relpath(root, src)
        if rel_path == ".":
            rel_path = ""

        # Remove ignored directories from the walk
        dirs[:] = [
            dir_name for dir_name in dirs
            if not ignored.match_file(path.join(root, dir_name))
        ]
        files[:] = [
            f for f in files if not ignored.match_file(path.join(root, f))
        ]

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
                absent_files.append(Link(path.join(root, f), pathname))

    return absent_files, absent_dirs


def link_folder(src, dest, force=False):
    """Link the folder src to the destination dest

    Args:
        src (path) - The path to link from
        dest (path) - The path to link to

    Returns:
        True if an operation was performed, else False
    """
    folder_name = path.basename(src).strip(".")

    try:
        # Both Folders Exist
        if path.exists(dest) and path.exists(src) and not path.islink(dest):
            if force or utils.user_confirm("Link and merge {} to {}".format(
                    src, dest)):
                absent_files, absent_dirs = find_absences(dest, src)
                zip_file = shutil.make_archive(
                    path.join(src, "{}_backup".format(folder_name)),
                    "zip",
                    root_dir=dest)
                logger.info("Backing up {} to {}".format(
                    folder_name, zip_file))
                utils.create_dirs(absent_dirs)
                logger.info("Created {}".format(absent_dirs))
                utils.move_files(absent_files)
                logger.info("Moving files {}".format(absent_files))
                shutil.rmtree(dest)
                logger.info("Removed {}".format(dest))
                os.symlink(src, dest)
                logger.info("Symlinked {} to {}".format(src, dest))
                return True

        # Only the source exists
        elif (not path.exists(dest) and not path.islink(dest)
              and path.exists(src)):
            try:
                dir_util.mkpath(path.dirname(dest), verbose=1)
            except distutils.errors.DistutilsFileError:
                logger.error("Failed to make dir {}".format(dest))
                return
            os.symlink(src, dest)
            logger.info("Symlinked {} to {}".format(src, dest))
            return True

        # Only the destination exists
        elif path.exists(dest) and not path.exists(src):
            if (force or utils.user_confirm("Delete, Move to {} and"
                                            " Link back to {}?".format(
                                                src, dest))):
                shutil.move(dest, src)
                logger.info("Moving {} to {}".format(dest, src))
                shutil.rmtree(dest)
                logger.info("Removed {}".format(dest))
                os.symlink(src, dest)
                logger.info("Symlinked {} to {}".format(src, dest))
                return True

        # Nothing to do
        return False

    except OSError:
        logger.error("Failed to link {} to {}".format(src, dest))
        return True


class Linker():
    """Tyler Stapler's Config Linker
    """

    def __init__(self, linker_config, prompt=True):

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
        if (not self.prompt
                or utils.user_confirm("Are these the correct files?")):
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
                if link_folder(file.src, file.dest, self.prompt):
                    modified = True
            if path.isfile(file.src):
                if utils.create_links([file]):
                    modified = True

        if not modified:
            logger.info("No folders to link")
