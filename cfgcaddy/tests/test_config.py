import os

import yaml

from cfgcaddy.config import LinkerConfig
from cfgcaddy.tests import FileLinkTestCase


class TestLinkerConfig(FileLinkTestCase):
    default_config = {}

    def test_no_config(self):
        os.remove(self.config_file_path)

        self.test_empty_config()

    def test_empty_config(self):
        with self.assertRaises(SystemExit) as cm:
            LinkerConfig(self.config_file_path)

        self.assertEqual(cm.exception.code, 1)

    def test_write_section(self):
        self.default_config = {
            "preferences": {
                "linker_src": self.source_dir,
                "linker_dest": self.dest_dir
            },
            "links": [],
            "ignore": []
        }

        linker_config = LinkerConfig(
            self.config_file_path, default_config=self.default_config)

        linker_config.write_config(prompt=False)

        output = {}

        with open(self.config_file_path) as file:
            output = yaml.load(file)

        print(output)

        self.assertDictEqual(self.default_config, output)
