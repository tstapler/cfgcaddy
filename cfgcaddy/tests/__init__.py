from functools import reduce
import operator
import os
import shutil
import tempfile
import unittest


def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)


def setInDict(dataDict, mapList, value):
    getFromDict(dataDict, mapList[:-1])[mapList[-1]] = value


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


def dir_dict(startpath):
    structure = {}
    for root, dirs, files in os.walk(startpath):
        current_level = os.path.relpath(root, startpath).split(os.sep)
        depth = len(current_level)
        if depth >= 1 and current_level[0] != '.':
            current_dict = getFromDict(structure, current_level)
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

        self.config_file_path = os.path.join(
            self.source_dir,
            ".cfgcaddy.yml"
        )

        open(self.config_file_path, 'a').close()

    def tearDown(self):
        shutil.rmtree(self.source_dir, onerror=handle_links)
        shutil.rmtree(self.dest_dir, onerror=handle_links)

    def recursive_dircmp(self, dircmp_obj):
        self.assertListEqual(dircmp_obj.left_only, [])
        self.assertListEqual(dircmp_obj.right_only, [])
        for dir_name, dir in dircmp_obj.subdirs.items():
            self.recursive_dircmp(dir)

    def assertDestMatchesExpected(self):
        dest_tree = dir_dict(self.dest_dir)

        self.assertEqual(self.expected_tree, dest_tree)
