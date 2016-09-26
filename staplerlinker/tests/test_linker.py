from staplerlinker.tests import (list_files, create_files_from_tree,
                                 FileLinkTestCase)


class TestLinker(FileLinkTestCase):
    def test_customlinks_file_absent(self):
        """Test when the custom links file doesn't exist"""
        pass
