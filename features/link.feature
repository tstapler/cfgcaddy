Feature: Link things
	Background: 
		Given a mocked home directory
		Given a file named ".cfgcaddy.yml" with:
		"""
		---
		preferences:
		  linker_src: $HOME/dotfiles
		  linker_dest: $HOME
		"""

	Scenario: The user is running cfgcaddy for the first time
		Given a directory containing:
		"""
		dotfiles
			.tmux.conf
			.vimrc
			wemux.conf
		"""
		When I run `cfgcaddy --debug link --no-prompt`
		Then the directory should contain the links:
		"""
		.tmux.conf
		.vimrc
		wemux.conf
		"""

