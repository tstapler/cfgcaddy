download-act:
	[ -f install.sh ] || wget https://raw.githubusercontent.com/nektos/act/v0.2.25/install.sh
	echo 21dc7689b4b3c9248a68bbed8796b1acc0e62cc3b33648d4c90561c72a1ea3c5  install.sh | sha256sum -c
	chmod +x install.sh
	sudo ./install.sh && rm install.sh
