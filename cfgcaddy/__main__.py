#!/usr/bin/env python
import logging
import os

import click

import cfgcaddy
import cfgcaddy.config
import cfgcaddy.utils
import linker

from whaaaaat import prompt

logger = logging.getLogger("cfgcaddy")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


config_questions = {
    "preferences": [
        {
            "type": "input",
            "name": "linker_src",
            "message": "Where are your config files located?",
            "validate": lambda p: p and os.path.isdir(
                cfgcaddy.utils.expand_path(p)
            )
        },
        {
            "type": "input",
            "name": "linker_dest",
            "message": "Where should your configs be linked to?",
            "default": cfgcaddy.HOME_DIR,
            "validate": lambda p: p and os.path.isdir(
                cfgcaddy.utils.expand_path(p)
            )
        }

        # TODO: Add additional preferences like what to do on a conflict
        # or the ability to use a basic ignore (.git, only .*, etc)
    ],
    "links": [],
    "ignore": []
}


def create_config(config_path, new_config={}):
    for section, questions in config_questions.items():
        if not new_config.get(section):
            new_config[section] = prompt(questions)
    config = cfgcaddy.config.LinkerConfig(config_file_path=config_path,
                                          default_config=new_config)
    config.write_config()
    return config


@click.group()
def main():
    """A tool for managing your configuration files"""
    pass


@main.command()
@click.option('-c', '--config',
              default=cfgcaddy.DEFAULT_CONFIG_PATH,
              help="The path to your cfgcaddy.yml")
def link(config):
    """Link your config files"""
    if not os.path.isfile(config):
        linker_config = create_config(config)
    else:
        linker_config = cfgcaddy.config.LinkerConfig(config_file_path=config)

    caddy = linker.Linker(linker_config)
    caddy.create_links()
    caddy.create_custom_links()


@main.command()
@click.argument('src_directory', type=click.Path(exists=True,
                                                 file_okay=False))
@click.argument('dest_directory', type=click.Path(exists=True,
                                                  file_okay=False))
@click.option('-c', '--config', type=click.Path(exists=True,
                                                dir_okay=False),
              help="The path to your cfgcaddy.yml")
def init(src_directory, dest_directory, config):
    """Create or import a caddy config"""
    src_config_path = os.path.join(src_directory, cfgcaddy.DEFAULT_CONFIG_NAME)

    if os.path.isfile(cfgcaddy.DEFAULT_CONFIG_PATH):
        logger.error("A cfgcaddy config is already present")
    elif config:
        symlink_config("provided", config, cfgcaddy.DEFAULT_CONFIG_PATH)
    elif os.path.exists(src_config_path):
        symlink_config(
            "existing", src_config_path, cfgcaddy.DEFAULT_CONFIG_PATH)
    else:
        create_config(
            cfgcaddy.DEFAULT_CONFIG_PATH, {
                "preferences": {
                    "linker_src": src_directory,
                    "linker_dest": dest_directory
                }
            })


def symlink_config(kind, src, dest):
    try:
        logger.info("Symlinking {} cfgcaddy config".format(kind))
        os.symlink(src, dest)
    except OSError:
        logger.error("Symlinking {} cfgcaddy config failed".format(kind))


if __name__ == '__main__':
    main(prog_name="cfgcaddy")
