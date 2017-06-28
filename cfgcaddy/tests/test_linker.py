from cfgcaddy.config import LinkerConfig
from cfgcaddy.linker import Linker
from cfgcaddy.tests import FileLinkTestCase, create_files_from_tree


class TestCustomLinker(FileLinkTestCase):

    def check_custom_link(self, line):
        create_files_from_tree(self.source_tree, parent=self.source_dir)
        create_files_from_tree(self.dest_tree, parent=self.dest_dir)

        config = {
            "preferences": {
                "linker_src": self.source_dir,
                "linker_dest": self.dest_dir
            },
            "links": [line],
            "ignore": [".*ignore.*"]
        }
        config = LinkerConfig(default_config=config)

        linker = Linker(config)

        linker.create_custom_links()

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

        self.check_custom_link("sub/*:folder")

    def test_basic_direct_copy(self):
        self.source_tree = {
            "other": "",
        }

        self.expected_tree = {
            "other": "",
        }

        self.check_custom_link("other")

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

        self.check_custom_link("*.test")

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

        self.check_custom_link("*.test:test_folder")

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

        self.check_custom_link("*.test:test_folder")

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

        self.check_custom_link("somefolder/*.test:test_folder")

    def test_rename_file(self):
        self.source_tree = {
            "last.test": "",
        }

        self.dest_tree = {
        }

        self.expected_tree = {
            "different.test": "",
        }

        self.check_custom_link("last.test:different.test")
