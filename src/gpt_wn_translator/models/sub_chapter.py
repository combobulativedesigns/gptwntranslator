from src.gpt_wn_translator.models.chunk import Chunk


class SubChapter:
    def __init__(self, sub_chapter_index, chapter_index, name, translated_name, link, release_date, contents, translation, chunks):
        if not isinstance(sub_chapter_index, int):
            raise TypeError("Index must be an integer")
        if not isinstance(chapter_index, int):
            raise TypeError("Chapter index must be an integer")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(translated_name, str):
            raise TypeError("Translated name must be a string")
        if not isinstance(link, str):
            raise TypeError("Link must be a string")
        if not isinstance(release_date, str):
            raise TypeError("Release date must be a string")
        if not isinstance(contents, str):
            raise TypeError("Contents must be a string")
        if not isinstance(translation, str):
            raise TypeError("Translation must be a string")
        if not isinstance(chunks, list(Chunk)):
            raise TypeError("Chunks must be a list of Chunk objects")
        
        self.sub_chapter_index = sub_chapter_index
        self.chapter_index = chapter_index
        self.name = name
        self.translated_name = translated_name
        self.link = link
        self.release_date = release_date
        self.contents = contents
        self.translation = translation
        self.chunks = chunks

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
