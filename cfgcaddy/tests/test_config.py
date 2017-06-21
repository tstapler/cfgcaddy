import os

import yaml
from mock import patch

from cfgcaddy.config import LinkerConfig
from cfgcaddy.tests import FileLinkTestCase


class TestLinkerConfig(FileLinkTestCase):
    default_config = {}

    def test_no_config(self):
        os.remove(self.config_file_path)

        self.test_empty_config()

    def test_empty_config(self):
        with self.assertRaises(SystemExit) as cm:
            LinkerConfig(self.config_file_path, prompt=False)

        self.assertEqual(cm.exception.code, 1)

    def test_write_section(self):
        self.default_config = {
            "preferences": {
                "linker_src": self.source_dir,
                "linker_dest": self.dest_dir
            },
            "links": {},
            "ignore": {}

        }

        linker_config = LinkerConfig(self.config_file_path,
                                     prompt=False,
                                     default_config=self.default_config)

        linker_config.write_config()

        output = {}

        with open(self.config_file_path) as file:
            output = yaml.load(file)

        self.assertDictEqual(self.default_config, output)

    @patch('inquirer.prompt')
    def test_load_section_inquire(self, prompt):
        pref_section = {
            "linker_src": self.source_dir,
            "linker_dest": self.dest_dir
        }

        self.default_config = {
            "preferences": pref_section
        }

        prompt.return_value = pref_section
        link_cfg = LinkerConfig(self.config_file_path,
                                prompt=False,
                                default_config=self.default_config)

        link_cfg.load_section("preferences")

        self.assertDictEqual(pref_section, link_cfg.config["preferences"])
