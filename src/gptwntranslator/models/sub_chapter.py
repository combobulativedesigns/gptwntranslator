"""Sub chapter model."""

from gptwntranslator.models.chunk import Chunk


class SubChapter:
    """This class represents a sub chapter in a chapter."""

    def __init__(self, novel_code: str, chapter_index: int, sub_chapter_index: int, link: str, name: str, contents: str, release_date: str, translated_name: str="", translation: str="", summary: str="", ) -> None:
        """Initialize a SubChapter object.

        Parameters
        ----------
        novel_code : str
            The code of the novel.
        chapter_index : int
            The index of the chapter.
        sub_chapter_index : int
            The index of the sub chapter.
        link : str
            The link to the sub chapter.
        name : str
            The name of the sub chapter.
        contents : str
            The contents of the sub chapter.
        release_date : str
            The release date of the sub chapter.
        translated_name : str, optional
            The translated name of the sub chapter, by default ""
        translation : str, optional
            The translation of the sub chapter, by default ""
        summary : str, optional
            The summary of the sub chapter, by default ""
        """
        
        # Validate parameters
        if not isinstance(novel_code, str):
            raise TypeError("Novel code must be a string")
        if not isinstance(chapter_index, int):
            raise TypeError("Chapter index must be an integer")
        if not isinstance(sub_chapter_index, int):
            raise TypeError("Index must be an integer")
        if not isinstance(link, str):
            raise TypeError("Link must be a string")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(contents, str):
            raise TypeError("Contents must be a string")
        if not isinstance(release_date, str):
            raise TypeError("Release date must be a string")
        if not isinstance(translated_name, str):
            raise TypeError("Translated name must be a string")
        if not isinstance(translation, str):
            raise TypeError("Translation must be a string")
        if not isinstance(summary, str):
            raise TypeError("Summary must be a string")
        
        # Set attributes
        self.novel_code = novel_code
        self.chapter_index = chapter_index
        self.sub_chapter_index = sub_chapter_index
        self.link = link
        self.name = name
        self.contents = contents
        self.release_date = release_date
        self.translated_name = translated_name
        self.translation = translation
        self.summary = summary

    def __str__(self):
        return f"Sub-chapter {self.sub_chapter_index} from chapter {self.chapter_index}"
    
    def __repr__(self):
        return f"Sub-chapter {self.sub_chapter_index} from chapter {self.chapter_index}"
    
    def __eq__(self, other):
        if not isinstance(other, SubChapter):
            raise TypeError("Other object must be a SubChapter object")
        if self.sub_chapter_index == other.sub_chapter_index and self.chapter_index == other.chapter_index:
            return True
        return False
    
    def __ne__(self, other):
        if not isinstance(other, SubChapter):
            raise TypeError("Other object must be a SubChapter object")
        if self.sub_chapter_index != other.sub_chapter_index or self.chapter_index != other.chapter_index:
            return True
        return False
    
    def __lt__(self, other):
        if not isinstance(other, SubChapter):
            raise TypeError("Other object must be a SubChapter object")
        if self.chapter_index < other.chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index < other.sub_chapter_index:
            return True
        return False
    
    def __le__(self, other):
        if not isinstance(other, SubChapter):
            raise TypeError("Other object must be a SubChapter object")
        if self.chapter_index < other.chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index <= other.sub_chapter_index:
            return True
        return False
    
    def __gt__(self, other):
        if not isinstance(other, SubChapter):
            raise TypeError("Other object must be a SubChapter object")
        if self.chapter_index > other.chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index > other.sub_chapter_index:
            return True
        return False
    
    def __ge__(self, other):
        if not isinstance(other, SubChapter):
            raise TypeError("Other object must be a SubChapter object")
        if self.chapter_index > other.chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index >= other.sub_chapter_index:
            return True
        return False
