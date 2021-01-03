# Config Caddy

![Travis CI](https://travis-ci.org/tstapler/cfgcaddy.svg?branch=master)
[![PyPI version](https://badge.fury.io/py/cfgcaddy.svg)](https://badge.fury.io/py/cfgcaddy)


Config Caddy is a tool used for managing your configuration files. 

One way to version your configuration files is to keep them in a [git](https://git-scm.com/) repository. This has several drawbacks, among them, git requires the files it manages to be located within a single file tree. You can overcome this limitation by using symbolic links. The links point from locations in your filesystem such as `/etc/someconfig.conf`to files within the git repository like `$HOME/tstapler/dotfiles/someconfig.conf`.

Config Caddy creates symlinks to your dotfiles directory, so you don't have to. Each time you add a new file to your dotfiles repo, run `cfgcaddy link` to generate symlinks. By default `cfgcaddy` will create links from files in the dotfiles repo to their relative location in your home directory. `cfgcaddy` will also read from a configuration file. This allows the user to ignore certain files and create more complex linking relationships.


## Usage

2. Install using pip

```shell

pip install cfgcaddy

````
2. Generate or import a configuration file for cfgcaddy

```shell
cfgcaddy init --help

Usage: cfgcaddy init [OPTIONS] SRC_DIRECTORY DEST_DIRECTORY

  Create or import a caddy config

Options:
  -c, --config PATH  The path to your cfgcaddy.yml
  --help             Show this message and exit.

cfgcaddy init $HOME/dotfiles $HOME
```

3. Run the linker
```bash
cfgcaddy link
```

## Configuration File Format

`cfgcaddy` uses a configuration file to store important information about your configuration. The `.cfgcaddy.yml` consists of several parts. A *preferences* section which contains information like where your dotfiles are located and where you want them linked to, A *links* section where you can specify more complex symlinks, and an `ignore` section where you specify files you do not want managed by `cfgcaddy`.

Config files for cfgcaddy are stored in your home directory by default. `$HOME/.cfgcaddy.yml`

A sample `.cfgcaddy.yml` which leverages most features can be found [here](https://github.com/tstapler/dotfiles/blob/master/.cfgcaddy.yml)

## Development

1. Clone the repository

```shell

git clone https://github.com/tstapler/cfgcaddy

```

2. Install cfgcaddy as an editable package

```shell

pip install --editable ./cfgcaddy

```

3. ??????

4. Profit

## Motivation/Prior Art

I'm an automation fiend, this tool grew out of a personal need to manage my configurations across multiple machines and operating systems. It fits my needs and I'll add features as I need them (Like Windows support). PRs are always welcome :)

Here are several projects that I've drawn inspiration from:

- https://github.com/charlesthomas/linker
- https://github.com/thoughtbot/rcm
