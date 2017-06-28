import logging
import os
from os import path
import glob
import sys

from ruamel.yaml import YAML

from link import Link
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


        if not self.linker_src or not self.linker_dest:
            logger.error("You need to specify a src and destination")
            sys.exit(1)

        self.generate_links(self.config["links"])

    @property
    def preferences(self):
        return self.config.get("preferences") or {}

    @property
    def linker_src(self):
        src = "linker_src"
        return self.preferences.get(src)

    @property
    def linker_dest(self):
        dest = "linker_dest"
        return self.preferences.get(dest)


    def write_config(self, prompt=True):
        if (not os.path.exists(self.config_file_path) or (not prompt or
            utils.user_confirm("The file {} exists.\n"
                               "Would you like to overwrite this file?"
                               .format(self.config_file_path)))):
            try:
                logger.debug("Writing File")
                yaml.dump(self, sys.stdout)
                with open(self.config_file_path, "w") as file:
                    logger.debug(self.config_file_path)
                    yaml.dump(self, file)
            except Exception as e:
                logger.error("Error writing config: {}".format(e))

    def read_config(self):
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, 'r') as file:
                self.config = yaml.load(file)

    def generate_links(self, links):
        custom_links = []

        #import ipdb; ipdb.sset_trace()
        for link in links:
            src = link
            destinations = [link]
            try:
                src = link.items()[0]
                destinations = link.items()[1]
            except:
                pass
            src_files = glob.glob(path.join(self.linker_src, src))
            for file in src_files:
                fname = path.basename(file)
                for dest in destinations:
                    destination = path.join(
                        self.linker_dest, dest)
                    if path.isdir(destination):
                        destination = path.join(destination, fname)

                        if not path.islink(destination):
                            trans = Link(
                                path.join(self.linker_src, file),
                                          path.join(destination))
                            custom_links.append(trans)

        logger.debug("Custom Links => {}".format(custom_links))
        self.links = custom_links

    @property
    def ignore_patterns(self):
        lines = self.config["ignore"]
        """Parse the gitignore style file

        Args:
            file_path (string): The path to the target file

        Returns:
            string: Returns the regexes derived from the file
        """
        if lines == []:
            return "a^"
        else:
            return "(" + ")|(".join(lines) + ")"  # regex from list of regexes
