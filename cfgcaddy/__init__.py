import os
from enum import Enum
from logging import getLogger

__version__ = "0.1.6"

logging = getLogger()
logging.propagate = True


class LinkMode(Enum):
    SKIP = "SKIP"
    OVERRIDE = "OVERRIDE"


DEFAULT_CONFIG_NAME = ".cfgcaddy.yml"

DEFAULT_DOTFILES_DIR = os.path.join(os.path.expanduser("~"), "dotfiles")

HOME_DIR = os.path.expanduser("~")
DEFAULT_CONFIG_PATH = os.path.join(HOME_DIR, DEFAULT_CONFIG_NAME)
