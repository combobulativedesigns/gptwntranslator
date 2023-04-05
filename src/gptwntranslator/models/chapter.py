"""Chapter model"""

from gptwntranslator.models.sub_chapter import SubChapter


class Chapter:
    """This class represents a chapter in a novel."""

    def __init__(self, novel_code: str, chapter_index: int, name: str, translated_name: str="", sub_chapters: list[SubChapter]=[]) -> None:
        """Initialize a Chapter object.

        Parameters
        ----------
        novel_code : str
            The code of the novel.
        chapter_index : int
            The index of the chapter.
        name : str
            The name of the chapter.
        translated_name : str, optional
            The translated name of the chapter, by default ""
        sub_chapters : list[SubChapter], optional
            The sub chapters of the chapter, by default []
        """

        # Validate parameters
        if not isinstance(novel_code, str):
            raise TypeError("Novel code must be a string")
        if not isinstance(chapter_index, int):
            raise TypeError("Chapter index must be an integer")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(translated_name, str):
            raise TypeError("Translated name must be a string")
        if not isinstance(sub_chapters, list):
            raise TypeError("Sub chapters must be a list")
        if not all(isinstance(sub_chapter, SubChapter) for sub_chapter in sub_chapters):
            raise TypeError("Sub chapters must be a list of SubChapter objects")
        
        # Set attributes
        self.novel_code = novel_code
        self.chapter_index = chapter_index
        self.name = name
        self.translated_name = translated_name
        self.sub_chapters = sub_chapters

    def get_sub_chapter(self, sub_chapter_index: int) -> SubChapter:
        """Return the sub chapter with the given index.

        Parameters
        ----------
        sub_chapter_index : int
            The index of the sub chapter.

        Returns
        -------
        SubChapter
            The sub chapter with the given index.
        """

        # Validate parameters
        if not isinstance(sub_chapter_index, int):
            raise TypeError("Sub chapter index must be an integer")
        
        # Return the sub chapter with the given index
        return [sub_chapter for sub_chapter in self.sub_chapters if sub_chapter.sub_chapter_index == sub_chapter_index][0]

    def __str__(self) -> str:
        """Return the string representation of a Chapter object."""

        return f"{self.chapter_index}"
    
    def __repr__(self) -> str:
        """Return the string representation of a Chapter object."""

        return f"Chapter {self.chapter_index}"
    
    def __eq__(self, other) -> bool:
        """Return True if the two Chapter objects are equal.

        Parameters
        ----------
        other : Chapter
            The other Chapter object to compare.
        """	

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index == other.chapter_index and self.novel_code == other.novel_code
    
    def __ne__(self, other) -> bool:
        """Return True if the two Chapter objects are not equal.

        Parameters
        ----------
        other : Chapter
            The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index != other.chapter_index and self.novel_code != other.novel_code
    
    def __lt__(self, other) -> bool:
        """Return True if the first Chapter object is less than the second.

        Parameters
        ----------
        other : Chapter
            The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        if self.novel_code != other.novel_code:
            raise ValueError("Cannot compare chapters from different novels")
        return self.chapter_index < other.chapter_index
    
    def __le__(self, other) -> bool:
        """Return True if the first Chapter object is less than or equal to the second.

        Parameters
        ----------
        other : Chapter
            The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        if self.novel_code != other.novel_code:
            raise ValueError("Cannot compare chapters from different novels")
        return self.chapter_index <= other.chapter_index
    
    def __gt__(self, other) -> bool:
        """Return True if the first Chapter object is greater than the second.

        Parameters
        ----------
        other : Chapter
            The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        if self.novel_code != other.novel_code:
            raise ValueError("Cannot compare chapters from different novels")
        return self.chapter_index > other.chapter_index
    
    def __ge__(self, other) -> bool:
        """Return True if the first Chapter object is greater than or equal to the second.

        Parameters
        ----------
        other : Chapter
            The other Chapter object to compare.
        """

        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        if self.novel_code != other.novel_code:
            raise ValueError("Cannot compare chapters from different novels")
        return self.chapter_index >= other.chapter_index