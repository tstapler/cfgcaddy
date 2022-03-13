from os import path

from cfgcaddy.link import Link
from tests import FileLinkTestCase, create_files_from_tree


class TestLink(FileLinkTestCase):
    def setup_files(self):
        create_files_from_tree(self.source_tree, parent=self.source_dir)
        create_files_from_tree(self.dest_tree, parent=self.dest_dir)

    def test_file_blocked(self):
        file_name = "test_file"
        self.source_tree = {file_name: ""}
        self.dest_tree = {file_name: ""}

        self.setup_files()

        link = Link(
            path.join(self.source_dir, file_name), path.join(self.dest_dir, file_name)
        )
        link.create()

        self.assertFalse(link.is_linked)

    def test_file_link(self):
        file_name = "test_file"

        self.source_tree = {file_name: ""}

        self.setup_files()

        link = Link(
            path.join(self.source_dir, file_name), path.join(self.dest_dir, file_name)
        )
        link.create()

        self.assertTrue(link.is_linked)
