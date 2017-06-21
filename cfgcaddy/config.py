import logging
import os
import sys

import inquirer
import yaml

import utils

logger = logging.getLogger("cfgcaddy.config")

MISSING_FILE_MESSAGE = "Please create a {} file in the same" \
    " directory as the linker python file."

DEFAULT_DOTFILES_DIR = os.path.join(os.path.expanduser("~"), "dotfiles")
HOME_DIR = os.path.expanduser("~")


class LinkerConfig():
    config = {}
    config_questions = {
        "preferences": [
            inquirer.Text(name="linker_src",
                          message="Where are your config files located?",
                          default=HOME_DIR,
                          validate=os.path.isdir),
            inquirer.Text(name="linker_dest",
                          message="Where should your configs be linked to?")

            # TODO: Add additional preferences like what to do on a conflict
            # or the ability to use a basic ignore (.git, only .*, etc)
        ],
        "custom_links": [],
        "ignore": []

    }

    modified = False

    def __init__(self,
                 config_file_path=None,
                 default_config=None,
                 prompt=True):
        self.config_file_path = config_file_path
        self.prompt = prompt

        if default_config:
            self.config = default_config
        elif self.config_file_path:
            self.read_config()

        # Don't continue if we wont prompt for the config
        if not self.prompt and not self.config:
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

        if not getattr(self, src) or not getattr(self, dest):
            raise Exception("You need to specify a src and destination")

    def load_section(self, section_name):
        if not self.config.get(section_name):
            section = {}
            if self.prompt:
                results = inquirer.prompt(
                    self.config_questions.get(section_name))
                if results:
                    section = results
                    self.config[section_name] = results
                    self.modifies = True
        else:
            section = self.config.get(section_name)

        setattr(self, section_name, section)

    def write_config(self):
        if (not os.path.exists(self.config_file_path) or
            not self.prompt or
                utils.user_confirm("Would you like to overwrite this file")):
            try:
                logger.debug("Writing File")
                logger.debug(yaml.dump(self.config))
                with open(self.config_file_path, "w") as file:
                    logger.debug(self.config_file_path)
                    file.write(yaml.dump(self.config))
            except Exception:
                logger.error("Could not write to {} because".format(Exception))

    def read_config(self):
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, 'r') as file:
                self.config = yaml.load(file)
