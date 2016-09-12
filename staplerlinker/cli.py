#!/usr/bin/python
import logging

import click

from linker import Linker

logger = logging.getLogger("stapler_linker")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


@click.command()
@click.argument("source", type=click.Path(exists=True), required=False)
@click.argument("destination", type=click.Path(exists=True), required=False)
def link(source, destination):
    """Link a folder of dotfiles to a home, or other specified directory"""
    linker = Linker(src=source, dest=destination)
    linker.link_configs()
    linker.create_custom_links()


if __name__ == '__main__':
    link()
