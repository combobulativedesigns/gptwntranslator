"""Chapter model"""

from gptwntranslator.models.sub_chapter import SubChapter


class Chapter:
    """Chapter model"""
    
    def __init__(self, chapter_index: int, name: str, translated_name: str, sub_chapters: list[SubChapter]) -> None:
        """
        Initialize a Chapter object.

        Arguments:
            chapter_index (int) - The index of the chapter.
            name (str) - The name of the chapter.
            translated_name (str) - The translated name of the chapter.
            sub_chapters (list[SubChapter]) - The list of sub-chapters in the chapter.
        """

        if not isinstance(chapter_index, int):
            raise TypeError("Index must be an integer")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(translated_name, str):
            raise TypeError("Translated name must be a string")
        if not isinstance(sub_chapters, list[SubChapter]):
            raise TypeError("Sub-chapters must be a list of SubChapter objects")
        
        self.chapter_index = chapter_index
        self.name = name
        self.translated_name = translated_name
        self.sub_chapters = sub_chapters

    def __str__(self) -> str:
        """Return the string representation of a Chapter object."""

        return f"Chapter {self.chapter_index}"
    
    def __repr__(self) -> str:
        """Return the string representation of a Chapter object."""

        return f"Chapter {self.chapter_index}"
    
    def __eq__(self, other) -> bool:
        """
        Return True if the two Chapter objects are equal.
        
        Arguments:
            other (Chapter) - The other Chapter object to compare.
        """	

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index == other.chapter_index
    
    def __ne__(self, other) -> bool:
        """
        Return True if the two Chapter objects are not equal.
        
        Arguments:
            other (Chapter) - The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index != other.chapter_index
    
    def __lt__(self, other) -> bool:
        """
        Return True if the first Chapter object is less than the second.
        
        Arguments:
            other (Chapter) - The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index < other.chapter_index
    
    def __le__(self, other) -> bool:
        """
        Return True if the first Chapter object is less than or equal to the second.
        
        Arguments:
            other (Chapter) - The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index <= other.chapter_index
    
    def __gt__(self, other) -> bool:
        """
        Return True if the first Chapter object is greater than the second.
        
        Arguments:
            other (Chapter) - The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index > other.chapter_index
    
    def __ge__(self, other) -> bool:
        """
        Return True if the first Chapter object is greater than or equal to the second.
        
        Arguments:
            other (Chapter) - The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index >= other.chapter_index