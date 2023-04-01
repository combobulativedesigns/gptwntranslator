"""Tests for the chunk module."""

import unittest
from gptwntranslator.models.chunk import Chunk


class TestChunk(unittest.TestCase):
    """Tests for the Chunk class."""

    def test_init(self) -> None:
        chunk = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        self.assertEqual(chunk.chunk_index, 1)
        self.assertEqual(chunk.chapter_index, 1)
        self.assertEqual(chunk.sub_chapter_index, 1)
        self.assertEqual(chunk.contents, "Contents")
        self.assertEqual(chunk.translation, "Translation")
        self.assertEqual(chunk.prev_line, "Prev line")
        self.assertEqual(chunk.next_line, "Next line")

    def test_init_invalid_arguments(self) -> None:
        with self.assertRaises(TypeError):
            Chunk("1", 1, 1, "Contents", "Translation", "Prev line", "Next line")

        with self.assertRaises(TypeError):
            Chunk(1, "1", 1, "Contents", "Translation", "Prev line", "Next line")

        with self.assertRaises(TypeError):
            Chunk(1, 1, "1", "Contents", "Translation", "Prev line", "Next line")

        with self.assertRaises(TypeError):
            Chunk(1, 1, 1, 1, "Translation", "Prev line", "Next line")

        with self.assertRaises(TypeError):
            Chunk(1, 1, 1, "Contents", 1, "Prev line", "Next line")

        with self.assertRaises(TypeError):
            Chunk(1, 1, 1, "Contents", "Translation", 1, "Next line")

        with self.assertRaises(TypeError):
            Chunk(1, 1, 1, "Contents", "Translation", "Prev line", 1)

    def test_str(self) -> None:
        chunk = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        self.assertEqual(str(chunk), "Chunk 1 from chapter 1 sub-chapter 1")

    def test_repr(self) -> None:
        chunk = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        self.assertEqual(repr(chunk), "Chunk 1 from chapter 1 sub-chapter 1")

    def test_eq(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertEqual(chunk1, chunk2)

    def test_ne_1(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(2, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertNotEqual(chunk1, chunk2)

    def test_ne_2(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 2, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertNotEqual(chunk1, chunk2)

    def test_ne_3(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 2, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertNotEqual(chunk1, chunk2)

    def test_lt_1(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(2, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertLess(chunk1, chunk2)

    def test_lt_2(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 2, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertLess(chunk1, chunk2)

    def test_lt_3(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 2, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertLess(chunk1, chunk2)

    def test_le_1(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(2, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertLessEqual(chunk1, chunk2)

    def test_le_2(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 2, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertLessEqual(chunk1, chunk2)

    def test_le_3(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 2, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertLessEqual(chunk1, chunk2)

    def test_le_4(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertLessEqual(chunk1, chunk2)

    def test_gt_1(self) -> None:
        chunk1 = Chunk(2, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertGreater(chunk1, chunk2)

    def test_gt_2(self) -> None:
        chunk1 = Chunk(1, 2, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertGreater(chunk1, chunk2)

    def test_gt_3(self) -> None:
        chunk1 = Chunk(1, 1, 2, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertGreater(chunk1, chunk2)

    def test_ge_1(self) -> None:
        chunk1 = Chunk(2, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertGreaterEqual(chunk1, chunk2)

    def test_ge_2(self) -> None:
        chunk1 = Chunk(1, 2, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertGreaterEqual(chunk1, chunk2)

    def test_ge_3(self) -> None:
        chunk1 = Chunk(1, 1, 2, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertGreaterEqual(chunk1, chunk2)

    def test_ge_4(self) -> None:
        chunk1 = Chunk(1, 1, 1, "Contents", "Translation", "Prev line", "Next line")
        chunk2 = Chunk(1, 1, 1, "Different", "Diferente", "Linea anterior", "Linea siguiente")
        self.assertGreaterEqual(chunk1, chunk2)


if __name__ == "__main__":
    unittest.main()

    
