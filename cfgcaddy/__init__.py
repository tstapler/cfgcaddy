import os
from enum import Enum

LINK_MODE = Enum("LINK_MODE", "SKIP OVERRIDE")

DEFAULT_CONFIG_NAME = ".cfgcaddy.yml"

DEFAULT_DOTFILES_DIR = os.path.join(os.path.expanduser("~"), "dotfiles")

HOME_DIR = os.path.expanduser("~")
DEFAULT_CONFIG_PATH = os.path.join(HOME_DIR, DEFAULT_CONFIG_NAME)
