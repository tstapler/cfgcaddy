import logging
import sys

from linker import Linker

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

if __name__ == '__main__':

    config_linker = Linker()

    config_linker.link_folders()
    config_linker.link_configs()
