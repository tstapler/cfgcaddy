import os
from filecmp import dircmp

from staplerlinker.linker import Linker
from staplerlinker.tests import (FileLinkTestCase,
                                 create_files_from_tree,
                                 dir_dict,
                                 list_files)


class TestCustomLinker(FileLinkTestCase):

    def setUp(self):
        super(TestCustomLinker, self).setUp()
        self.source_tree = {
            "other": "",
            "something.test": "",
            "another.test": "",
            "last.test": "",
            "folder": {
            },
            "sub": {
                "file1": "",
                "file2": "",
                "file3": "",
            }
        }

        self.dest_tree = {
            "test_folder": {
            },
        }

        self.expected_tree = {
            "other": "",
            "something.test": "",
            "another.test": "",
            "last.test": "",
            "different.test": "",
            "folder": {
                "file1": "",
                "file2": "",
                "file3": "",
            },
            "test_folder": {
                "something.test": "",
                "another.test": "",
                "last.test": "",
            },
        }

        create_files_from_tree(self.source_tree, parent=self.source_dir)
        create_files_from_tree(self.dest_tree, parent=self.dest_dir)

        self.links_file = os.path.join(self.source_dir, ".customlinks")
        with open(self.links_file, 'w') as f:
            f.write("*.test\n")
            f.write("*.test:test_folder\n")
            f.write("last.test:different.test\n")
            f.write("other\n")
            f.write("sub/*:folder\n")

    def test_customlinks_file_absent(self):
        """Test when the custom links file doesn't exist"""
        pass

    def test_customlinks_parser(self):
        """Test that the custom linker does globbing correctly"""
        linker = Linker(src=self.source_dir,
                        dest=self.dest_dir)

        links = linker._parse_customlinks(self.links_file)

        self.assertEqual(len(links), 11)

    def test_customlinks(self):
        """Test that the custom linker does globbing correctly"""
        linker = Linker(src=self.source_dir,
                        dest=self.dest_dir)

        linker.create_custom_links()

        print(list_files(self.source_dir))
        print(list_files(self.dest_dir))

        dest_tree = dir_dict(self.dest_dir)

        self.assertEqual(self.expected_tree, dest_tree)
