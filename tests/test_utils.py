from filecmp import dircmp

from cfgcaddy.linker import link_folder
from tests import FileLinkTestCase, create_files_from_tree, list_files


class TestLinkFolder(FileLinkTestCase):
    def recursive_dircmp(self, dircmp_obj):
        self.assertListEqual(dircmp_obj.left_only, [])
        self.assertListEqual(dircmp_obj.right_only, [])
        for dir_name, sub_dir in dircmp_obj.subdirs.items():
            self.recursive_dircmp(sub_dir)

    def link_and_print(self):
        print("Before:")
        list_files(self.source_dir)
        list_files(self.dest_dir)

        link_folder(self.source_dir, self.dest_dir, force=True)

        print("\nAfter:")
        list_files(self.source_dir)
        list_files(self.dest_dir)

    def test_both_dirs_exist(self):
        self.source_tree = {
            "file1": "stuff",
            "file2": "stuff",
            "dir1": {"file3": "stuff"},
        }
        self.dest_tree = {
            "file4": "stuff",
            "file5": "stuff",
            "dir2": {"file6": "stuff"},
        }

        create_files_from_tree(self.source_tree, parent=self.source_dir)
        create_files_from_tree(self.dest_tree, parent=self.dest_dir)
        self.link_and_print()
        result = dircmp(self.source_dir, self.dest_dir)
        self.recursive_dircmp(result)

    def test_destination_exists(self):
        self.dest_tree = {
            "file1": "stuff",
            "file2": "stuff",
            "dir1": {"file3": "stuff"},
        }
        create_files_from_tree(self.dest_tree, parent=self.dest_dir)
        self.link_and_print()
        dircmp(self.source_dir, self.dest_dir)
        result = dircmp(self.source_dir, self.dest_dir)
        self.recursive_dircmp(result)

    def test_source_exists(self):
        self.source_tree = {
            "file1": "stuff",
            "file2": "stuff",
            "dir1": {"file3": "stuff"},
        }
        create_files_from_tree(self.source_tree, parent=self.source_dir)
        self.link_and_print()
        dircmp(self.source_dir, self.dest_dir)
        result = dircmp(self.source_dir, self.dest_dir)
        self.recursive_dircmp(result)
