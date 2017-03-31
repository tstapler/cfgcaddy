#!/usr/bin/env python
import argparse
import logging

import linker

logger = logging.getLogger("stapler_linker")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description="Link Dotfiles to "
                                             "a specified directory")
parser.add_argument("--src", action="store",
                    dest="source", default=linker.DEFAULT_DOTFILES_DIR)
parser.add_argument("--dest", action="store",
                    dest="destination", default=linker.DEFAULT_HOME_DIR)


def link(source, destination):
    """Link a folder of dotfiles to a home, or other specified directory"""
    config_linker = linker.Linker(src=source, dest=destination)
    config_linker.link_configs()
    config_linker.create_custom_links()


if __name__ == '__main__':
    results = parser.parse_args()
    link(results.source, results.destination)
