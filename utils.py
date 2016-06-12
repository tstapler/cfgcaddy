from os import makedirs, symlink
import sys


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
        return ""
    else:
        return "(" + ")|(".join(lines) + ")"  # regex from list of regexes


def create_dirs(dirs=[]):
    """Creates all folders in dirs

    Args:
        dirs ([string]): A list of paths to be linked

    Returns:
        None: Does not return anything
    """
    for dir_name in dirs:
        makedirs(dir_name)


def create_links(links=[]):
    """Create symlinks for each item in links

    Args:
        links([Link]): a list of Links
    Returns:
        None: Does not return anything
    """
    for link in links:
        symlink(link.src, link.dest)


def sync_dir(dir):
    """Recursively syncronizes two directories"""
    pass
