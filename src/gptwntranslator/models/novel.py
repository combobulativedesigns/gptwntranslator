from gptwntranslator.models.chapter import Chapter


class Novel:
    def __init__(self, novel_code, title, title_translation, author, author_translation, author_link, description, description_translation, chapters):
        if not isinstance(novel_code, str):
            raise TypeError("Novel code must be a string")
        if not isinstance(title, str):
            raise TypeError("Title must be a string")
        if not isinstance(title_translation, str):
            raise TypeError("Title translation must be a string")
        if not isinstance(author, str):
            raise TypeError("Author must be a string")
        if not isinstance(author_translation, str):
            raise TypeError("Author translation must be a string")
        if not isinstance(author_link, str):
            raise TypeError("Author link must be a string")
        if not isinstance(description, str):
            raise TypeError("Description must be a string")
        if not isinstance(description_translation, str):
            raise TypeError("Description translation must be a string")
        if not isinstance(chapters, list):
            raise TypeError("Chapters must be a list of Chapter objects")
        
        self.novel_code = novel_code
        self.title = title
        self.title_translation = title_translation
        self.author = author
        self.author_translation = author_translation
        self.author_link = author_link
        self.description = description
        self.description_translation = description_translation
        self.chapters = chapters

    def __str__(self):
        return f"Novel {self.novel_code}"
    
    def __repr__(self):
        return f"Novel {self.novel_code}"