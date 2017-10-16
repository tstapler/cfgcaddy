test:
	nosetests

watch-acceptance:
	docker build . -t tstapler/cfgcaddy-testing
	docker run -it -v $(PWD):/cfgcaddy tstapler/cfgcaddy-testing sh -c \
		"cd cfgcaddy && guard"
