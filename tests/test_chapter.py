"""Tests for the Chapter class."""

import unittest
from gptwntranslator.models.chapter import Chapter


class TestChapter(unittest.TestCase):
    """Tests for the Chapter class."""

    def test_init(self) -> None:
        """Test that the Chapter class is initialized correctly."""
        
        chapter = Chapter(1, "Introduction", "Introducción", [])
        self.assertEqual(chapter.chapter_index, 1)
        self.assertEqual(chapter.name, "Introduction")
        self.assertEqual(chapter.translated_name, "Introducción")
        self.assertEqual(chapter.sub_chapters, [])

    def test_init_invalid_arguments(self) -> None:
        """Test that the Chapter class raises the correct exceptions."""

        with self.assertRaises(TypeError):
            Chapter("1", "Introduction", "Introducción", [])

        with self.assertRaises(TypeError):
            Chapter(1, 1, "Introducción", [])

        with self.assertRaises(TypeError):
            Chapter(1, "Introduction", 1, [])

        with self.assertRaises(TypeError):
            Chapter(1, "Introduction", "Introducción", "[]")

    def test_str(self) -> None:
        """Test that the Chapter class returns the correct string."""

        chapter = Chapter(1, "Introduction", "Introducción", [])
        self.assertEqual(str(chapter), "Chapter 1")

    def test_repr(self) -> None:
        """Test that the Chapter class returns the correct representation."""	

        chapter = Chapter(1, "Introduction", "Introducción", [])
        self.assertEqual(repr(chapter), "Chapter 1")

    def test_eq(self) -> None:
        """Test that the Chapter class returns the correct equality."""

        chapter1 = Chapter(1, "Introduction", "Introducción", [])
        chapter2 = Chapter(1, "Different", "Diferente", [])
        self.assertEqual(chapter1, chapter2)

    def test_ne(self) -> None:
        """Test that the Chapter class returns the correct inequality."""

        chapter1 = Chapter(1, "Introduction", "Introducción", [])
        chapter2 = Chapter(2, "Different", "Diferente", [])
        self.assertNotEqual(chapter1, chapter2)

    def test_lt(self) -> None:
        """Test that the Chapter class returns the correct less than."""

        chapter1 = Chapter(1, "Introduction", "Introducción", [])
        chapter2 = Chapter(2, "Different", "Diferente", [])
        self.assertLess(chapter1, chapter2)

    def test_le_1(self) -> None:
        """Test that the Chapter class returns the correct less than or equal."""

        chapter1 = Chapter(1, "Introduction", "Introducción", [])
        chapter2 = Chapter(1, "Different", "Diferente", [])
        self.assertLessEqual(chapter1, chapter2)

    def test_le_2(self) -> None:
        """Test that the Chapter class returns the correct less than or equal."""

        chapter1 = Chapter(1, "Introduction", "Introducción", [])
        chapter2 = Chapter(2, "Different", "Diferente", [])
        self.assertLessEqual(chapter1, chapter2)

    def test_gt(self) -> None:
        """Test that the Chapter class returns the correct greater than."""

        chapter1 = Chapter(2, "Different", "Diferente", [])
        chapter2 = Chapter(1, "Introduction", "Introducción", [])
        self.assertGreater(chapter1, chapter2)

    def test_ge_1(self) -> None:
        """Test that the Chapter class returns the correct greater than or equal."""

        chapter1 = Chapter(1, "Introduction", "Introducción", [])
        chapter2 = Chapter(1, "Different", "Diferente", [])
        self.assertGreaterEqual(chapter1, chapter2)

    def test_ge_2(self) -> None:
        """Test that the Chapter class returns the correct greater than or equal."""

        chapter1 = Chapter(2, "Different", "Diferente", [])
        chapter2 = Chapter(1, "Introduction", "Introducción", [])
        self.assertGreaterEqual(chapter1, chapter2)


if __name__ == "__main__":
    unittest.main()