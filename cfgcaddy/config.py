import glob
import logging
import os
import platform
import sys
from os import path

import yaml

from cfgcaddy import utils
from cfgcaddy.link import Link

logger = logging.getLogger("cfgcaddy.config")

MISSING_FILE_MESSAGE = "Please create a {} file in the same" \
    " directory as the linker python file."


class LinkerConfig():
    config = None
    links = []

    def __init__(self, config_file_path=None, default_config=None):
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

        self.generate_links(self.links_yaml)

    @property
    def preferences(self):
        return self.config.get("preferences") or {}

    @property
    def linker_src(self):
        src = "linker_src"
        return utils.expand_path(self.preferences.get(src))

    @property
    def linker_dest(self):
        dest = "linker_dest"
        return utils.expand_path(self.preferences.get(dest))

    def write_config(self, prompt=True):
        if (not os.path.exists(self.config_file_path) or
            (not prompt
             or utils.user_confirm("The file {} exists.\n"
                                   "Would you like to overwrite this file?"
                                   .format(self.config_file_path)))):
            try:
                logger.info("Writing config file")
                with open(self.config_file_path, "w") as file:
                    logger.debug(self.config_file_path)
                    yaml.dump(self.config, file)
            except Exception as e:
                logger.error("Error writing config: {}".format(e))

    def read_config(self):
        if os.path.isfile(self.config_file_path):
            with open(self.config_file_path, 'r') as file:
                self.config = yaml.load(file)

    def generate_links(self, links):
        custom_links = []

        for link in links:
            try:
                if link.get("os") and platform.system() not in link.get("os"):
                    logger.debug("OS: {}".format(link.get("os")))
                    continue

                link_src = utils.expand_path(link["src"])
                link_dests = link.get("dest")
                src_files = glob.glob(path.join(self.linker_src, link_src))

                # To account for no destination
                if not link_dests:
                    if len(src_files) > 1:
                        link_dests = [path.dirname(link_src)]
                    else:
                        link_dests = [link_src]
                for src_path in src_files:
                    for dest in map(utils.expand_path, link_dests):
                        if len(src_files) > 1:
                            src_name = path.join(dest, path.basename(src_path))
                        else:
                            src_name = dest
                        if path.isabs(dest):
                            dest_path = src_name
                        else:
                            dest_path = path.join(self.linker_dest, src_name)
                        custom_links.append(
                            Link(
                                utils.expand_path(src_path),
                                utils.expand_path(dest_path)))
            except KeyError:
                logger.exception("Bad custom link")

        logger.debug("Custom Links => {}".format(custom_links))
        self.links = custom_links

    @property
    def links_yaml(self):
        """Parse the YAML config representation into a consistent format"""
        links = []
        for link in self.config.get("links", []):
            if type(link) is str:
                link = {"src": link, "dest": []}
            if type(link.get("dest")) is str:
                link["dest"] = [link["dest"]]
            links.append(link)
        logger.debug("Links before formatting: {}".format(
            self.config.get("links")))
        logger.debug("Links after formatting: {}".format(links))
        return links

    @property
    def ignore_patterns(self):
        lines = self.config.get("ignore", [])
        """Parse the gitignore style file
        """
        logger.debug("Ignore Patterns: {}".format(lines))
        return lines
