from pathlib import Path

from cfgcaddy import config, linker


def test_files_in_src_are_linked_without_config(tmp_path: Path):
    dotfiles_dir = Path(tmp_path, "dotfiles")
    dotfiles_dir.mkdir()

    target_dotfiles = [".zshrc", ".tmux", ".zplug_plugins"]
    for file in target_dotfiles:
        Path(dotfiles_dir, file).touch()

    config_file = Path(tmp_path, ".cfgcaddy.yml")
    config_value = f"""---
preferences:
  linker_src: {str(dotfiles_dir)}
  linker_dest: {str(tmp_path)}
"""
    config_file.write_text(config_value)

    linker_config = config.LinkerConfig(config_file_path=config_file)

    caddy = linker.Linker(linker_config, interactive=False)
    caddy.create_links()
    caddy.create_custom_links()

    for file in target_dotfiles:
        assert Path(tmp_path, file).is_symlink()
