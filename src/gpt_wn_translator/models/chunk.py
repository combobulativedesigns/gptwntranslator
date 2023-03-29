from src.gpt_wn_translator.models.term_sheet import TermSheet

class Chunk:
    def __init__(self, chunk_index, chapter_index, sub_chapter_index, contents, term_sheet, summary, translation, translation_fixed):
        if not isinstance(chunk_index, int):
            raise TypeError("Index must be an integer")
        if not isinstance(chapter_index, int):
            raise TypeError("Chapter index must be an integer")
        if not isinstance(sub_chapter_index, int):
            raise TypeError("Sub-chapter index must be an integer")
        if not isinstance(contents, str):
            raise TypeError("Contents must be a string")
        if not isinstance(term_sheet, TermSheet):
            raise TypeError("Term sheet must be a TermSheet object")
        if not isinstance(summary, str):
            raise TypeError("Summary must be a string")
        if not isinstance(translation, str):
            raise TypeError("Translation must be a string")
        if not isinstance(translation_fixed, str):
            raise TypeError("Fixed translation must be a string")
        
        self.chunk_index = chunk_index
        self.chapter_index = chapter_index
        self.sub_chapter_index = sub_chapter_index
        self.contents = contents
        self.term_sheet = term_sheet
        self.summary = summary
        self.translation = translation
        self.translation_fixed = translation_fixed
    
    def __str__(self):
        return f"Chunk {self.chunk_index} from chapter {self.chapter_index} sub-chapter {self.sub_chapter_index}"
    
    def __repr__(self):
        return f"Chunk {self.chunk_index} from chapter {self.chapter_index} sub-chapter {self.sub_chapter_index}"
    
    def __eq__(self, other):
        if not isinstance(other, Chunk):
            raise TypeError("Other object must be a Chunk object")
        if self.chunk_index == other.chunk_index and self.chapter_index == other.chapter_index and self.sub_chapter_index == other.sub_chapter_index:
            return True
        return False
    
    def __ne__(self, other):
        if not isinstance(other, Chunk):
            raise TypeError("Other object must be a Chunk object")
        if self.chunk_index != other.chunk_index or self.chapter_index != other.chapter_index or self.sub_chapter_index != other.sub_chapter_index:
            return True
        return False
    
    def __lt__(self, other):
        if not isinstance(other, Chunk):
            raise TypeError("Other object must be a Chunk object")
        if self.chapter_index < other.chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index < other.sub_chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index == other.sub_chapter_index and self.chunk_index < other.chunk_index:
            return True
        return False
    
    def __le__(self, other):
        if not isinstance(other, Chunk):
            raise TypeError("Other object must be a Chunk object")
        if self.chapter_index < other.chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index < other.sub_chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index == other.sub_chapter_index and self.chunk_index <= other.chunk_index:
            return True
        return False
    
    def __gt__(self, other):
        if not isinstance(other, Chunk):
            raise TypeError("Other object must be a Chunk object")
        if self.chapter_index > other.chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index > other.sub_chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index == other.sub_chapter_index and self.chunk_index > other.chunk_index:
            return True
        return False
    
    def __ge__(self, other):
        if not isinstance(other, Chunk):
            raise TypeError("Other object must be a Chunk object")
        if self.chapter_index > other.chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index > other.sub_chapter_index:
            return True
        elif self.chapter_index == other.chapter_index and self.sub_chapter_index == other.sub_chapter_index and self.chunk_index >= other.chunk_index:
            return True
        return False