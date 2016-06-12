from collections import namedtuple
from os import makedirs, symlink, walk
from os.path import relpath, join, exists
from shutil import move
import sys
import re


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
            if not exists(join(dest, rel_path, dir_name)):
                absent_dirs.append(join(dest, rel_path, dir_name))

        # Create a list of files to be symlinked
        for f in files:
            if not exists(join(dest, rel_path, f)):
                # Add the source and destination for the symlink
                absent_files.append(Transaction(join(root, f),
                                    join(dest, rel_path, f)))

    return absent_files, absent_dirs


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

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

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
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
    except IOError:
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
            makedirs(dir_name)


def create_links(links=None):
    """Create symlinks for each item in links

    Args:
        links([Transaction]): a list of paths to link
    Returns:
        None: Does not return anything
    """
    if links:
        for link in links:
            symlink(link.src, link.dest)


def move_files(transactions=None):
    """Move the files in the list from src to dest

    Args:
        transactions([Transaction])

    Returns:
        None: Does not return anything
    """
    if transactions:
        for transaction in transactions:
            move(transaction.src, transaction.dest)


