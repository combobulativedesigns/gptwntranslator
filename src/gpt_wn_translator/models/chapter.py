from src.gpt_wn_translator.models.sub_chapter import SubChapter


class Chapter:
    def __init__(self, chapter_index, name, translated_name, sub_chapters):
        if not isinstance(chapter_index, int):
            raise TypeError("Index must be an integer")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if not isinstance(translated_name, str):
            raise TypeError("Translated name must be a string")
        if not isinstance(sub_chapters, list):
            raise TypeError("Sub-chapters must be a list of SubChapter objects")
        
        self.chapter_index = chapter_index
        self.name = name
        self.translated_name = translated_name
        self.sub_chapters = sub_chapters

    def __str__(self):
        return f"Chapter {self.chapter_index}"
    
    def __repr__(self):
        return f"Chapter {self.chapter_index}"
    
    def __eq__(self, other):
        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index == other.chapter_index
    
    def __ne__(self, other):
        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index != other.chapter_index
    
    def __lt__(self, other):
        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index < other.chapter_index
    
    def __le__(self, other):
        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index <= other.chapter_index
    
    def __gt__(self, other):
        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index > other.chapter_index
    
    def __ge__(self, other):
        if not isinstance(other, Chapter):
            raise TypeError("Other object must be a Chapter object")
        return self.chapter_index >= other.chapter_index