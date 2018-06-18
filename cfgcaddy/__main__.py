#!/usr/bin/env python
import ctypes
import logging
import os
import platform
import sys

import click
from whaaaaat import prompt

import cfgcaddy
import cfgcaddy.config
import cfgcaddy.utils
import cfgcaddy.linker

logger = logging.getLogger("cfgcaddy")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

config_questions = {
    "preferences":
    [{
        "type": "input",
        "name": "linker_src",
        "message": "Where are your config files located?",
        "validate":
        lambda p: p and os.path.isdir(cfgcaddy.utils.expand_path(p))
    }, {
        "type": "input",
        "name": "linker_dest",
        "message": "Where should your configs be linked to?",
        "default": cfgcaddy.HOME_DIR,
        "validate":
        lambda p: p and os.path.isdir(cfgcaddy.utils.expand_path(p))
    }

     # TODO: Add additional preferences like what to do on a conflict
     # or the ability to use a basic ignore (.git, only .*, etc)
     ],
}

default_config = {"links": [], "ignore": []}


def create_config(config_path, new_config=None):
    logger.debug("default_config: {}".format(new_config))

    if not new_config:
        new_config = default_config

    for section, questions in config_questions.items():
        if not new_config.get(section):
            new_config[section] = prompt(questions)

    logger.debug("Creating Config => {}".format(new_config))

    config = cfgcaddy.config.LinkerConfig(
        config_file_path=config_path, default_config=new_config)
    config.write_config()
    return config


@click.group()
@click.option('-d', '--debug', is_flag=True, help="Enable Debugging output")
@click.option('-q', '--quiet', is_flag=True, help="Silence cfgcaddy")
def main(debug, quiet):
    """A tool for managing your configuration files"""
    if debug:
        logger.setLevel(logging.DEBUG)
    if quiet:
        logger.setLevel(logging.ERROR)


@main.command()
@click.option(
    '-c',
    '--config',
    default=cfgcaddy.DEFAULT_CONFIG_PATH,
    help="The path to your cfgcaddy.yml")
@click.option('-y', '--no-prompt', is_flag=True)
def link(config, no_prompt):
    """Link your config files"""
    if not os.path.isfile(config):
        logger.error(
            "Cannot find cfgcaddy.yml, please specify path to config using '-c' option or create/link a new config using the 'cfgcaddy init' command."
        )
        return
    else:
        linker_config = cfgcaddy.config.LinkerConfig(config_file_path=config)

    caddy = cfgcaddy.linker.Linker(linker_config, prompt=not no_prompt)
    caddy.create_links()
    caddy.create_custom_links()


@main.command()
@click.argument('src_directory', type=click.Path(exists=True, file_okay=False))
@click.argument(
    'dest_directory', type=click.Path(exists=True, file_okay=False))
@click.option(
    '-c',
    '--config',
    type=click.Path(exists=True, dir_okay=False),
    help="The path to your cfgcaddy.yml")
def init(src_directory, dest_directory, config):
    """Create or import a caddy config"""
    src_config_path = os.path.join(src_directory, cfgcaddy.DEFAULT_CONFIG_NAME)

    if os.path.isfile(cfgcaddy.DEFAULT_CONFIG_PATH):
        logger.error("A cfgcaddy config is already present")
    elif config:
        symlink_config("provided", config, cfgcaddy.DEFAULT_CONFIG_PATH)
    elif os.path.exists(src_config_path):
        symlink_config("existing", src_config_path,
                       cfgcaddy.DEFAULT_CONFIG_PATH)
    else:
        default_config.update({
            "preferences": {
                "linker_src": src_directory,
                "linker_dest": dest_directory
            }
        })
        create_config(cfgcaddy.DEFAULT_CONFIG_PATH, default_config)


def symlink_config(kind, src, dest):
    try:
        os.symlink(src, dest)
        logger.info("Symlinking {} cfgcaddy config".format(kind))
    except OSError:
        logger.error("Symlinking {} cfgcaddy config failed".format(kind))
        if platform.system() == "Windows":
            logger.error(
                "Ensure that cfgcaddy is being run as an Administrator.\n"
                "By default, only administrators can create Symlinks on Windows."
            )


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == '__main__':
    if platform.system() == "Windows" and not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "",
                                            None, 1)
    main(prog_name="cfgcaddy")
