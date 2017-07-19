# Config Caddy

A tool to manage your configuration files.


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
