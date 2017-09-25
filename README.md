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

## Configuration File Format

Config files for cfgcaddy are stored in your home directory by default. `$HOME/.cfgcaddy.yml`

```yaml

preferences:
  linker_src: $HOME/dotfiles # Where your dotfiles are stored
  linker_dest: $HOME # Where to link dotfiles to
links:
  - src: .vimsnippets # You can link to multiple destinations
    dest:
      - .vimsnippets
      - .vim/bundle/.dein/stapler-snips
# Links the folder $HOME/dotfiles/.mixxx/controllers 
# to $HOME/.mixxx/controllers
  - src: .mixxx/controllers 
# Links all the files within $HOME/dotfiles/bin/scripts to
# a folder called $HOME/bin/scripts. This method can be used 
# to merge files from multiple folders
  - src: bin/scripts/*
    dest: bin/scripts
# Run only on the given os as defined by:
# https://docs.python.org/2/library/platform.html#platform.system
    os: "Linux Darwin"
  - src: .vimrc
    dest: .config/nvim/init.vim
    os: "Linux Darwin"
  - src: stapler-scripts/*
    dest: bin/scripts
    os: "Linux Darwin"
  - src: stapler-scripts/PowerShell
# You can use environment variables in the paths
# back slashes need to be escaped per yaml rules
    dest: "%userprofile%\\My Documents\\WindowsPowerShell\\"
    os: "Windows"
  - src: .vimrc
    dest: "%userprofile%\\AppData\\Local\\nvim\\init.vim"
    os: "Windows"
    # Symlinks for git are broken on windows
  - src: .gittemplates
    os: "Linux Darwin"
  - src: .vim/spell
  - src: .shell
    os: "Linux Darwin"
  - src: .tmux/*

ignore:
  # Globbing patterns to ignore when
  # linking config files to home dir
  - "*stapler*"
  - "cfgcaddy"
  - "*.git"
  - "*.swp"
  - "*.yml"
  - "*.zip"
  - "tags"
  - "nerd-fonts"
  - ".gittemplates"

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
