import os

from staplerlinker.linker import Linker
from staplerlinker.tests import (FileLinkTestCase,
                                 create_files_from_tree,
                                 list_files)


class TestCustomLinker(FileLinkTestCase):
    def setUp(self):
        super(TestCustomLinker, self).setUp()
        self.source_tree = {
            "other": "stuff",
            "something.test": "stuff",
            "another.test": "stuff",
            "last.test": "stuff",
            "folder": {}
        }

        self.dest_tree = {
            "test_folder": {}
        }

        create_files_from_tree(self.source_tree, parent=self.source_dir)
        create_files_from_tree(self.dest_tree, parent=self.dest_dir)

        self.links_file = os.path.join(self.source_dir, ".customlinks")
        with open(self.links_file, 'w') as f:
            f.write("*.test\n")
            f.write("*.test:test_folder\n")
            f.write("last.test:different.test\n")
            f.write("other")
            f.write("folder")

    def test_customlinks_file_absent(self):
        """Test when the custom links file doesn't exist"""
        pass

    def test_customlinks_parser(self):
        """Test that the custom linker does globbing correctly"""
        linker = Linker(src=self.source_dir,
                        dest=self.dest_dir)

        links = linker._parse_customlinks(self.links_file)

        self.assertEqual(len(links), 8)

    def test_customlinks(self):
        """Test that the custom linker does globbing correctly"""
        linker = Linker(src=self.source_dir,
                        dest=self.dest_dir)

        linker.create_custom_links()

        print(list_files(self.source_dir))
        print(list_files(self.dest_dir))
