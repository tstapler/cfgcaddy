import os
import platform
import yaml

from cfgcaddy.config import LinkerConfig
from cfgcaddy.linker import Linker
from cfgcaddy.tests import FileLinkTestCase, create_files_from_tree


def convert_link_format(line):
    """Convert from the old linker format to the new format
    src:dest => {src: dest}
    """
    output = line.split(':')

    if len(output) == 1:
        return line
    else:
        return {
            "src": output[0],
            "dest": output[1:]
        }


class TestCustomLinker(FileLinkTestCase):

    def setup_linker(self, config):
        create_files_from_tree(self.source_tree, parent=self.source_dir)
        create_files_from_tree(self.dest_tree, parent=self.dest_dir)

        with open(self.config_file_path, "w") as f:
            yaml.dump(config, f)

        cfg = LinkerConfig(config_file_path=self.config_file_path)

        return Linker(cfg, prompt=False)

    def check_custom_linker(self, *lines):

        config = {
            "preferences": {
                "linker_src": self.source_dir,
                "linker_dest": self.dest_dir
            },
            "links": [convert_link_format(line)
                      for line in lines],
            "ignore": ["*ignore*"]
        }

        linker = self.setup_linker(config)

        linker.create_custom_links()

        self.assertDestMatchesExpected()

    def check_basic_linker(self, links=[], ignore=["*ignore*"]):
        config = {
            "preferences": {
                "linker_src": self.source_dir,
                "linker_dest": self.dest_dir
            },
            "links": links,
            "ignore": ignore
        }

        linker = self.setup_linker(config)

        linker.create_links()

        self.assertDestMatchesExpected()

    def test_subdirectory_glob(self):
        self.source_tree = {
            "sub": {
                "file1": "",
                "file2": "",
                "file3": "",
            }
        }

        self.expected_tree = {
            "folder": {
                "file1": "",
                "file2": "",
                "file3": "",
            }
        }

        self.check_custom_linker("sub/*:folder")

    def test_basic_direct_copy(self):
        self.source_tree = {
            "other": "",
        }

        self.expected_tree = {
            "other": "",
        }

        self.check_custom_linker("other")

    def test_basic_glob(self):
        """docstring for test_basic_glob"""

        self.source_tree = {
            "something.test": "",
            "another.test": "",
            "last.test": "",
        }

        self.expected_tree = {
            "something.test": "",
            "another.test": "",
            "last.test": "",
        }

        self.check_custom_linker("*.test")

    def test_basic_glob_to_existing_folder(self):
        """docstring for test_basic_glob_to_folder"""

        self.source_tree = {
            "something.test": "",
            "another.test": "",
            "last.test": "",
        }

        self.dest_tree = {
            "test_folder": {
            }
        }

        self.expected_tree = {
            "test_folder": {
                "something.test": "",
                "another.test": "",
                "last.test": "",
            },
        }

        self.check_custom_linker("*.test:test_folder")

    def test_basic_glob_to_non_existing_folder(self):
        """docstring for test_basic_glob_to_folder"""

        self.source_tree = {
            "something.test": "",
            "another.test": "",
            "last.test": "",
        }

        self.expected_tree = {
            "test_folder": {
                "something.test": "",
                "another.test": "",
                "last.test": "",
            },
        }

        self.check_custom_linker("*.test:test_folder")

    def test_glob_folder_contents_to_folder(self):
        """docstring for test_basic_glob_to_folder"""

        self.source_tree = {
            "somefolder": {
                "something.test": "",
                "another.test": "",
                "last.test": "",
            }
        }

        self.dest_tree = {
            "test_folder": {
                "existingfile.test": ""
            }
        }

        self.expected_tree = {
            "test_folder": {
                "something.test": "",
                "another.test": "",
                "last.test": "",
                "existingfile.test": ""
            },
        }

        self.check_custom_linker("somefolder/*.test:test_folder")

    def test_rename_file(self):
        self.source_tree = {
            "last.test": "",
        }

        self.expected_tree = {
            "different.test": "",
        }

        self.check_custom_linker("last.test:different.test")

    def test_deep_copy(self):
        self.source_tree = {
            ".mixxx": {
                "controllers": {}
            }
        }

        self.expected_tree = {
            ".mixxx": {
                "controllers": {}
            }
        }

        self.check_custom_linker(".mixxx/controllers")

    def test_nested_glob(self):
        self.source_tree = {
            "bin": {
                "scripts": {
                    "script1": "",
                    "script2": "",
                    "script3": "",
                }
            },
            "stapler-scripts": {
                "script4": "",
                "script5": "",
                "script6": "",
            }
        }

        self.expected_tree = {
            "bin": {
                "scripts": {
                    "script1": "",
                    "script2": "",
                    "script3": "",
                    "script4": "",
                    "script5": "",
                    "script6": "",
                }
            }
        }

        self.check_custom_linker("bin/scripts/*:bin/scripts",
                                 "stapler-scripts/*:bin/scripts")

    def test_basic_linker(self):
        self.source_tree = {
            "test1": "",
            "test2": "",
            "test3": "",
            "test4": "",
            "test5": "",
            "test6": "",
            "ignore.file": ""
        }

        self.expected_tree = {
            "test1": "",
            "test2": "",
            "test3": "",
            "test4": "",
            "test5": "",
            "test6": "",
        }

        self.check_basic_linker()

    def test_subdirectory_ignore(self):
        self.source_tree = {
            ".git": {
                "test1": "",
                "test2": "",
                "test3": "",
                "test4": "",

            },
            "top": {
                "sub1": "",
                "sub2": "",
                "sub3": "",
                ".git": {
                    "test1": "",
                    "test2": "",
                    "test3": "",
                    "test4": "",
                }
            }
        }

        self.expected_tree = {
            "top":
                {
                    "sub1": "",
                    "sub2": "",
                    "sub3": "",
                }
        }

        self.check_basic_linker()

    def test_env_expand(self):
        self.source_tree = {
            "first": ""
        }

        self.expected_tree = {
            "da": {
                "real": {
                    "location": ""
                }
            }
        }

        dest = "da/real/location"

        os.environ["FILE_DEST"] = dest

        env_var = "$FILE_DEST"

        if platform.system() == "Windows":
            env_var = "%FILE_DEST%"

        self.check_custom_linker("first:{}".format(env_var))
