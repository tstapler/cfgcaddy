import logging

from linker import Linker

logger = logging.getLogger("stapler-linker")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

if __name__ == '__main__':

    config_linker = Linker()

    config_linker.link_folders()
    config_linker.link_configs()
