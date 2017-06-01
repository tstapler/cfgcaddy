import os
import shutil
import tempfile
import unittest


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


def handle_links(function, path, execinfo):
    if function is os.path.islink:
        os.unlink(path)


def create_files_from_tree(tree, parent=''):
    for name, content in tree.iteritems():
        name = os.path.join(parent, name)
        if type(content) is dict:
            os.makedirs(name)
            create_files_from_tree(content, parent=name)
        else:
            open(name, 'a').close()


class FileLinkTestCase(unittest.TestCase):
    def setUp(self):
        self.source_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        links_file = os.path.join(self.source_dir, ".customlinks")
        ignore_file = os.path.join(self.source_dir, ".linkerignore")
        open(links_file, 'a').close()
        open(ignore_file, 'w').close()

    def tearDown(self):
        shutil.rmtree(self.source_dir, onerror=handle_links)
        shutil.rmtree(self.dest_dir, onerror=handle_links)
