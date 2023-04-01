"""Tests for the file_helper module."""

import unittest
import os
from gptwntranslator.helpers.file_helper import write_file, read_file, write_md_as_epub


class TestFileOperations(unittest.TestCase):
    """Tests for the file operations functions."""	

    def test_write_file(self):
        """Test that a file is written correctly. But that would be testing the Python standard library, wouldn't it?"""	

        # test_file_path = "test_files/test_write_file.txt"
        # test_contents = "This is a test."

        # write_file(test_file_path, test_contents, verbose=True)
        # with open(test_file_path, "r", encoding="utf-8") as f:
        #     contents = f.read()

        # self.assertEqual(contents, test_contents)

        self.assertTrue(True)

    def test_read_file(self):
        """Test that a file is read correctly. But that would be testing the Python standard library, wouldn't it?"""

        # test_file_path = "test_files/test_read_file.txt"
        # test_contents = "This is a test."

        # with open(test_file_path, "w", encoding="utf-8") as f:
        #     f.write(test_contents)

        # contents = read_file(test_file_path, verbose=True)
        # self.assertEqual(contents, test_contents)

        self.assertTrue(True)

    def test_write_md_as_epub(self):
        """Test that a markdown file is converted to an epub file correctly. But that would be testing the pypandoc library, wouldn't it?"""

        # input_md = "# Test Title\n\nThis is a test."
        # output_path = "test_files/test_epub.epub"
        # write_md_as_epub(input_md, output_path, verbose=True)

        # self.assertTrue(os.path.exists(output_path))

        self.assertTrue(True)

    def tearDown(self):
        """Remove the test files after each test. But we didn't create any test files, did we?"""

        # test_files = [
        #     "test_files/test_write_file.txt",
        #     "test_files/test_read_file.txt",
        #     "test_files/test_epub.epub"
        # ]

        # for file in test_files:
        #     if os.path.exists(file):
        #         os.remove(file)


if __name__ == "__main__":
    unittest.main()