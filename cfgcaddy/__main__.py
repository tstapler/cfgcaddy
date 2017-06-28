#!/usr/bin/env python
import logging
import os

import click
import inquirer

import cfgcaddy
import cfgcaddy.config
import linker

logger = logging.getLogger("cfgcaddy")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


def expand_path(path):
    return os.path.expandvars(os.path.expanduser(path))


config_questions = {
    "preferences": [
        inquirer.Text(name="linker_src",
                      message="Where are your config files located?",
                      validate=lambda _, p: os.path.isdir(expand_path(p))),
        inquirer.Text(name="linker_dest",
                      message="Where should your configs be linked to?",
                      default=cfgcaddy.HOME_DIR,
                      validate=lambda _, p: os.path.isdir(expand_path(p)))

        # TODO: Add additional preferences like what to do on a conflict
        # or the ability to use a basic ignore (.git, only .*, etc)
    ],
    "links": [],
    "ignore": []

}


def create_config(config_path):
    new_config = {}
    for section, questions in config_questions.items():
        new_config[section] = inquirer.prompt(questions)
    logger.info(new_config)
    config = cfgcaddy.config.LinkerConfig(config_file_path=config_path,
                                          default_config=new_config)
    config.write_config()
    return config


@click.group(name="cfgcaddy")
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
@click.argument('src_directory', type=click.Path(exists=True))
@click.argument('dest_directory', type=click.Path(exists=True))
@click.option('-c', '--config',
              help="The path to your cfgcaddy.yml")
def init(src_directory, dest_directory, config):
    """Create or import a caddy config"""
    if os.path.isfile(cfgcaddy.DEFAULT_CONFIG_PATH):
        logger.info("A cfgcaddy config is already present")
    elif os.path.isfile(config):
        try:
            os.symlink(config, cfgcaddy.DEFAULT_CONFIG_PATH)
        except OSError:
            logger.error("Symlinking existing cfgcaddy config failed")
    elif os.path.isdir(src_directory) and os.path.isdir(dest_directory):
        pass


if __name__ == '__main__':
    main()
