from collections import namedtuple
import os
from os import makedirs, symlink, walk, unlink
from os.path import relpath, join, exists, isdir, isfile, islink, basename, dirname
from shutil import move, make_archive, rmtree
from distutils import dir_util
import distutils
import sys
import re
import logging

logger = logging.getLogger("stapler_linker.utils")

Transaction = namedtuple('Transaction', ['src', 'dest'])


def find_absences(src, dest, ignored_patterns="a^"):
    """ Walk the source directory and return a lists of files and dirs absent
        from the destination directory

    Args:
        source: The path to copy from (Default is the script's location)
        destination The path to copy to (Defaults to home directory)

    Returns:
        absent_files: a list of Transactions
        absent_dirs: a list of paths to directories
    """
    absent_dirs = []
    absent_files = []
    for root, dirs, files in walk(src, topdown=True):
        rel_path = relpath(root, src)
        if rel_path == ".":
            rel_path = ""

        # Remove ignored directories from the walk
        dirs[:] = [dir_name for dir_name in dirs
                   if not re.match(ignored_patterns, dir_name)]
        files[:] = [f for f in files
                    if not re.match(ignored_patterns, f)]

        # Create list of dirs that dont exist
        for dir_name in dirs:
            pathname = join(dest, rel_path, dir_name)
            if not exists(pathname):
                if islink(pathname):
                    unlink(pathname)  # Fix Broken Links
                absent_dirs.append(pathname)

        # Create a list of files to be symlinked
        for f in files:
            pathname = join(dest, rel_path, f)
            if not exists(pathname):
                if islink(pathname):
                    unlink(pathname)  # Fix Broken Links
                # Add the source and destination for the symlink
                absent_files.append(Transaction(join(root, f),
                                    pathname))

    return absent_files, absent_dirs


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via and return their answer.

    Args:
        question (string): a string that is presented to the user.
        default (string): the answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    Returns "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    global input
    try: input = raw_input
    except NameError: pass
    while True:
        # Fix Python 2.x.
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def get_lines_from_file(file_path):
    """ Return a list of lines from a file minus comments

    Args:
        file_path (string): The path to the target file

    Returns:
        [string]
    """
    try:
        return [line.split("#", 1)[0].strip("\n")
                for line in open(file_path)
                if line.split("#", 1)[0] != ""]
    except OSError:
        return [""]


def parse_regex_file(file_path):
    """Parse the gitignore style file

    Args:
        file_path (string): The path to the target file

    Returns:
        string: Returns the regexes derived from the file
    """
    lines = get_lines_from_file(file_path)
    if lines == []:
        return "a^"
    else:
        return "(" + ")|(".join(lines) + ")"  # regex from list of regexes


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
                makedirs(dir_name)
            except OSError:
                logger.error("Unable to create directory: {}", dir_name)


def make_parent_dirs(path):
    try:
        os.makedirs(dirname(path))
    except OSError as exc:  # Python >2.5
        pass

def create_links(links=None):
    """Create symlinks for each item in links

    Args:
        links([Transaction]): a list of paths to link
    Returns:
        None: Does not return anything
    """
    if links:
        for link in links:
            try:
                make_parent_dirs(link.dest)
                symlink(link.src, link.dest)
            except (OSError) as err:
                logger.error("Can't make link from {} to {} because {}"
                             .format(link.src, link.dest, err.strerror))


def move_files(transactions=None):
    """Move the files in the list from src to dest

    Args:
        transactions([Transaction])

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
    folder_name = basename(src).strip(".")

    try:
        # Both Folders Exist
        if exists(dest) and exists(src) and not islink(dest):
            if force or query_yes_no("Link and merge {} to {}"
                                     .format(src, dest)):
                absent_files, absent_dirs = find_absences(dest, src)
                zip_file = make_archive(join(src, "{}_backup".format(folder_name)),
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
                symlink(src, dest)
                logger.info("Symlinked {} to {}".format(src,
                                                        dest))
                return True

        # Only the source exists
        elif not exists(dest) and not islink(dest) and exists(src):
            try:
                dir_util.mkpath(dirname(dest), verbose=1)
            except (distutils.errors.DistutilsFileError, err):
                logger.error("Failed to make dir of {}".format(dest),
                             exc_info=True)
                return
            symlink(src, dest)
            logger.info("Symlinked {} to {}".format(src, dest))
            return True

        # Only the destination exists
        elif exists(dest) and not exists(src):
            if force or query_yes_no("Delete, Move to {} and Link back to {}?"
                                     .format(src, dest)):
                move(dest, src)
                logger.info("Moving {} to {}".format(dest, src))
                rmtree(dest)
                logger.info("Removed {}".format(dest))
                symlink(src, dest)
                logger.info("Symlinked {} to {}".format(src, dest))
                return True

        # Nothing to do
        return False

    except OSError:
        logger.error("Failed to link {} to {}".format(src,
                     dest), exc_info=True)
        return True
