import logging
import os
import shutil
from os import path

from whaaaaat import prompt

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
    return prompt([{
        "type": "confirm",
        "name": "ok",
        "message": question,
        "default": default
    }]).get("ok")


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
                # If the file exists and isn't a link
                if err.errno == 17 and not os.path.islink(link.dest):
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
                shutil.move(transaction.src, transaction.dest)
            except OSError:
                logger.error("Can't move from {} to {}".format(
                    transaction.src, transaction.dest))


def expand_path(path):
    return os.path.expandvars(os.path.expanduser(path))
