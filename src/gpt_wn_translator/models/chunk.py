from src.gpt_wn_translator.models.term_sheet import TermSheet

class Chunk:
    def __init__(self, chunk_index, chapter_index, sub_chapter_index, contents, translation, prev_line, next_line):
        if not isinstance(chunk_index, int):
            raise TypeError("Index must be an integer")
        if not isinstance(chapter_index, int):
            raise TypeError("Chapter index must be an integer")
        if not isinstance(sub_chapter_index, int):
            raise TypeError("Sub-chapter index must be an integer")
        if not isinstance(contents, str):
            raise TypeError("Contents must be a string")
        if not isinstance(translation, str):
            raise TypeError("Translation must be a string")
        if not isinstance(prev_line, str):
            raise TypeError("Previous line must be a string")
        if not isinstance(next_line, str):
            raise TypeError("Next line must be a string")
        
        self.chunk_index = chunk_index
        self.chapter_index = chapter_index
        self.sub_chapter_index = sub_chapter_index
        self.contents = contents
        self.translation = translation
        self.prev_line = prev_line
        self.next_line = next_line
    
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