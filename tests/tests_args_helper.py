"""Tests for the args_helper module."""

import unittest
from gptwntranslator.helpers.args_helper import parse_chapters


class TestParseChapters(unittest.TestCase):
    """Tests for the parse_chapters function."""

    def test_single_chapter(self):
        """Test that a single chapter is parsed correctly."""	
        input_string = "3"
        expected_output = {"3": []}
        self.assertEqual(parse_chapters(input_string), expected_output)

    def test_chapter_range(self):
        """Test that a chapter range is parsed correctly."""	
        input_string = "2-4"
        expected_output = {"2": [], "3": [], "4": []}
        self.assertEqual(parse_chapters(input_string), expected_output)

    def test_single_chapter_with_subchapters(self):
        """Test that a single chapter with subchapters is parsed correctly."""
        input_string = "5:1,2,3"
        expected_output = {"5": ["1", "2", "3"]}
        self.assertEqual(parse_chapters(input_string), expected_output)

    def test_single_chapter_with_subchapter_range(self):
        """Test that a single chapter with a subchapter range is parsed correctly."""
        input_string = "6:2-5"
        expected_output = {"6": ["2", "3", "4", "5"]}
        self.assertEqual(parse_chapters(input_string), expected_output)

    def test_multiple_chapters_and_ranges(self):
        """Test that multiple chapters and ranges are parsed correctly."""
        input_string = "1;3:1-3;4:1-2,5-6;5:2,4-6"
        expected_output = {
            "1": [],
            "3": ["1", "2", "3"],
            "4": ["1", "2", "5", "6"],
            "5": ["2", "4", "5", "6"],
        }
        self.assertEqual(parse_chapters(input_string), expected_output)

    def test_empty_input(self):
        """Test that an empty input string returns an empty dictionary."""
        input_string = ""
        expected_output = {}
        self.assertEqual(parse_chapters(input_string), expected_output)

    def test_invalid_input_1(self):
        """Test that an invalid input string raises a ValueError."""
        input_string = "1-2:2-3"
        with self.assertRaises(ValueError):
            parse_chapters(input_string)

    def test_invalid_input_2(self):
        """Test that an invalid input string raises a ValueError."""
        input_string = "1,2,3"
        with self.assertRaises(ValueError):
            parse_chapters(input_string)

    def test_invalid_input_3(self):
        """Test that an invalid input string raises a ValueError."""
        input_string = "1:2:3;4:5-6"
        with self.assertRaises(ValueError):
            parse_chapters(input_string)


if __name__ == "__main__":
    unittest.main()