import logging
import os
import sys

from ruamel.yaml import YAML

import utils

logger = logging.getLogger("cfgcaddy.config")

MISSING_FILE_MESSAGE = "Please create a {} file in the same" \
    " directory as the linker python file."


yaml = YAML()


class LinkerConfig():
    config = {}

    def __init__(self,
                 config_file_path=None,
                 default_config=None):
        self.config_file_path = config_file_path

        if default_config:
            self.config = default_config
        elif self.config_file_path:
            self.read_config()

        # Don't continue if we don't have a config
        if not self.config:
            logger.error("No config has been provided or loaded")
            sys.exit(1)

        self.load_section("preferences")
        self.load_section("links")
        self.load_section("ignore")

        src = "linker_src"
        if self.preferences.get(src):
            setattr(self, src, self.preferences.get(src))

        dest = "linker_dest"
        if self.preferences.get(dest):
            setattr(self, dest, self.preferences.get(dest))

        try:
            getattr(self, src) and getattr(self, dest)
        except AttributeError:
            logger.error("You need to specify a src and destination")
            sys.exit(1)

    def load_section(self, section_name):
        if not self.config.get(section_name):
            section = {}
        else:
            section = self.config.get(section_name)

        setattr(self, section_name, section)

    def write_config(self, prompt=True):
        if (not os.path.exists(self.config_file_path) or (not prompt or
            utils.user_confirm("The file {} exists.\n"
                               "Would you like to overwrite this file?"
                               .format(self.config_file_path)))):
            try:
                logger.debug("Writing File")
                yaml.dump(self.config, sys.stdout)
                with open(self.config_file_path, "w") as file:
                    logger.debug(self.config_file_path)
                    yaml.dump(self.config, file)
            except Exception as e:
                logger.error("Error writing config: {}".format(e))

    def read_config(self):
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, 'r') as file:
                self.config = yaml.load(file)
