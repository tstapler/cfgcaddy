import distutils
import logging
import os
import re
from distutils import dir_util
from os import path
from shutil import make_archive, move, rmtree

import inquirer

logger = logging.getLogger("cfgcaddy.utils")


def user_confirm(question, default=True):
    """Ask the user to confirm a choice

    Args:
        question (string): a string that is presented to the user.
        default (string): the answer if the user just hits <Enter>.
            It must be True, False or None (meaning
            an answer is required of the user).

    Returns "answer" return value is True for "yes" or False for "no".
    """
    return inquirer.prompt([
        inquirer.Confirm(name="ok", message=question,  default=default)
    ]).get("ok")


def create_dirs(dirs=None):
    """Creates all folders in dirs

    Args:
        dirs ([string]): A list of paths to be linked

    Returns:
        None: Does not return anything
    """
    if dirs:
        for dir_name in dirs:
            try:
                os.makedirs(dir_name)
            except OSError:
                logger.error("Unable to create directory: {}", dir_name)


def make_parent_dirs(file_path):
    try:
        os.makedirs(path.dirname(file_path))
    except OSError:  # Python >2.5
        pass


def create_links(links=None):
    """Create symlinks for each item in links

    Args:
        links([Link]): a list of paths to link
    Returns:
        None: Does not return anything
    """
    if links:
        for link in links:
            try:
                make_parent_dirs(link.dest)
                os.symlink(link.src, link.dest)
            except (OSError) as err:
                logger.error("Can't make link from {} to {} because {}"
                             .format(link.src, link.dest, err.strerror))


def move_files(transactions=None):
    """Move the files in the list from src to dest

    Args:
        transactions([Link])

    Returns:
        None: Does not return anything
    """
    if transactions:
        for transaction in transactions:
            try:
                move(transaction.src, transaction.dest)
            except OSError:
                logger.error("Can't move from {} to {}"
                             .format(transaction.src, transaction.dest))


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
            if force or user_confirm("Link and merge {} to {}"
                                     .format(src, dest)):
                absent_files, absent_dirs = find_absences(dest, src)
                zip_file = make_archive(
                    path.join(src, "{}_backup".format(folder_name)),
                                        "zip",
                                        root_dir=dest)
                logger.info("Backing up {} to {}".format(folder_name,
                                                         zip_file))
                create_dirs(absent_dirs)
                logger.info("Created {}".format(absent_dirs))
                move_files(absent_files)
                logger.info("Moving files {}".format(absent_files))
                rmtree(dest)
                logger.info("Removed {}".format(dest))
                os.symlink(src, dest)
                logger.info("Symlinked {} to {}".format(src,
                                                        dest))
                return True

        # Only the source exists
        elif not path.exists(dest) and not path.islink(dest) and path.exists(src):
            try:
                dir_util.mkpath(path.dirname(dest), verbose=1)
            except (distutils.errors.DistutilsFileError, err):
                logger.error("Failed to make dir of {}".format(dest),
                             exc_info=True)
                return
            os.symlink(src, dest)
            logger.info("Symlinked {} to {}".format(src, dest))
            return True

        # Only the destination exists
        elif path.exists(dest) and not path.exists(src):
            if force or user_confirm("Delete, Move to {} and Link back to {}?"
                                     .format(src, dest)):
                move(dest, src)
                logger.info("Moving {} to {}".format(dest, src))
                rmtree(dest)
                logger.info("Removed {}".format(dest))
                os.symlink(src, dest)
                logger.info("Symlinked {} to {}".format(src, dest))
                return True

        # Nothing to do
        return False

    except OSError:
        logger.error("Failed to link {} to {}".format(src,
                     dest), exc_info=True)
        return True


def expand_path(path):
    return os.path.expandvars(os.path.expanduser(path))
