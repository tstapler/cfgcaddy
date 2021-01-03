from functools import reduce
import operator
import os
import shutil
import tempfile
import unittest


def get_from_dict(data_dict, map_list):
    return reduce(operator.getitem, map_list, data_dict)


def set_in_dict(data_dict, map_list, value):
    get_from_dict(data_dict, map_list[:-1])[map_list[-1]] = value


def list_files(start_path):
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print('{}{}/'.format(indent, os.path.basename(root)))
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(sub_indent, f))


def dir_dict(start_path):
    structure = {}
    for root, dirs, files in os.walk(start_path):
        current_level = os.path.relpath(root, start_path).split(os.sep)
        depth = len(current_level)
        if depth >= 1 and current_level[0] != '.':
            current_dict = get_from_dict(structure, current_level)
        else:
            current_dict = structure

        for d in dirs:
            current_dict[d] = {}
        for f in files:
            current_dict[f] = ""
    return structure


def handle_links(function, path, execinfo):
    if function is os.path.islink:
        os.unlink(path)


def create_files_from_tree(tree, parent=''):
    for name, content in tree.items():
        name = os.path.join(parent, name)
        if type(content) is dict:
            os.makedirs(name)
            create_files_from_tree(content, parent=name)
        else:
            open(name, 'a').close()


class FileLinkTestCase(unittest.TestCase):
    def setUp(self):
        self.source_dir = tempfile.mkdtemp()
        self.source_tree = {}

        self.dest_dir = tempfile.mkdtemp()
        self.dest_tree = {}

        self.expected_tree = {}

        self.config_file_path = os.path.join(self.source_dir, ".cfgcaddy.yml")

        open(self.config_file_path, 'a').close()

    def tearDown(self):
        shutil.rmtree(self.source_dir, onerror=handle_links)
        shutil.rmtree(self.dest_dir, onerror=handle_links)

    def recursive_dircmp(self, dircmp_obj):
        self.assertListEqual(dircmp_obj.left_only, [])
        self.assertListEqual(dircmp_obj.right_only, [])
        for directory, sub_directory in dircmp_obj.subdirs.items():
            self.recursive_dircmp(sub_directory)

    def assertDestMatchesExpected(self):
        dest_tree = dir_dict(self.dest_dir)

        self.assertEqual(self.expected_tree, dest_tree)
