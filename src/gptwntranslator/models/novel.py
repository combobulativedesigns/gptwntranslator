"""Novel model."""

from types import NoneType
from gptwntranslator.models.chapter import Chapter
from gptwntranslator.models.term_sheet import TermSheet


class Novel:
    """Model for a japanese web novel."""

    def __init__(self, novel_code: str, title: str, author: str, description: str, original_language: str, title_translation: dict[str, str]={}, author_translation: dict[str, str]={}, author_link: str="", description_translation: dict[str, str]={}, chapters: list[Chapter]=[], terms_sheet: TermSheet|NoneType=None) -> None:
        """Initialize a novel object.

        Parameters
        ----------
        novel_code : str
            The code of the novel.
        title : str
            The title of the novel.
        author : str
            The author of the novel.
        description : str
            The description of the novel.
        original_language : str
            The original language of the novel.
        title_translation : str, optional
            The translation of the title, by default ""
        author_translation : str, optional
            The translation of the author, by default ""
        author_link : str, optional
            The link to the author's website, by default ""
        description_translation : str, optional
            The translation of the description, by default ""
        chapters : list[Chapter], optional
            The list of chapters in the novel, by default []
        terms_sheet : TermSheet|NoneType, optional
            The terms sheet of the novel, by default None
        """

        # Validate parameters
        if not isinstance(novel_code, str):
            raise TypeError("Novel code must be a string")
        if not isinstance(title, str):
            raise TypeError("Title must be a string")
        if not isinstance(author, str):
            raise TypeError("Author must be a string")
        if not isinstance(description, str):
            raise TypeError("Description must be a string")
        if not isinstance(original_language, str):
            raise TypeError("Original language must be a string")
        if not isinstance(title_translation, dict):
            raise TypeError("Title translation must be a dictionary")
        if not all(isinstance(key, str) for key in title_translation.keys()):
            raise TypeError("Title translation keys must be strings")
        if not all(isinstance(value, str) for value in title_translation.values()):
            raise TypeError("Title translation values must be strings")
        if not isinstance(author_translation, dict):
            raise TypeError("Author translation must be a dictionary")
        if not all(isinstance(key, str) for key in author_translation.keys()):
            raise TypeError("Author translation keys must be strings")
        if not all(isinstance(value, str) for value in author_translation.values()):
            raise TypeError("Author translation values must be strings")
        if not isinstance(author_link, str):
            raise TypeError("Author link must be a string")
        if not isinstance(description_translation, dict):
            raise TypeError("Description translation must be a dictionary")
        if not all(isinstance(key, str) for key in description_translation.keys()):
            raise TypeError("Description translation keys must be strings")
        if not all(isinstance(value, str) for value in description_translation.values()):
            raise TypeError("Description translation values must be strings")
        if not isinstance(chapters, list):
            raise TypeError("Chapters must be a list of Chapter objects")
        if not all(isinstance(chapter, Chapter) for chapter in chapters):
            raise TypeError("Chapters must be a list of Chapter objects")
        if not isinstance(terms_sheet, (NoneType, TermSheet)):
            raise TypeError("Terms sheet must be a TermSheet object or None")

        # Set attributes
        self.novel_code = novel_code
        self.title = title
        self.author = author
        self.description = description
        self.original_language = original_language
        self.title_translation = title_translation
        self.author_translation = author_translation
        self.author_link = author_link
        self.description_translation = description_translation
        self.chapters = chapters
        self.terms_sheet = terms_sheet if terms_sheet is not None else TermSheet(novel_code)

    def get_chapter(self, chapter_number: int) -> Chapter:
        """Return the chapter object of the given chapter number.

        Parameters
        ----------
        chapter_number : int
            The chapter number of the chapter to return.

        Returns
        -------
        Chapter
            The chapter object of the given chapter number.
        """

        # Validate parameters
        if not isinstance(chapter_number, int):
            raise TypeError("Chapter number must be an integer")

        # Return the chapter object
        return [chapter for chapter in self.chapters if chapter.chapter_index == chapter_number][0]
    
    def original_body(self) -> str:
        """Return the whole body of text available for this novel.

        Returns
        -------
        str
            The whole body of text available for this novel.
        """

        # Return the whole body of text available
        body = self.title
        for chapter in self.chapters:
            body += "\n\n"
            body += chapter.original_body()

        return body

    def __str__(self):
        """Return the string representation of a Novel object."""
        return f"{self.novel_code}"
    
    def __repr__(self):
        """Return the string representation of a Novel object."""
        return f"Novel {self.novel_code}"
    
    def __eq__(self, other):
        """Return True if the two Novel objects are equal.

        Parameters
        ----------
        other : Novel
            The other Novel object to compare.
        """

        if not isinstance(other, Novel):
            raise TypeError("Other object must be a Novel object")
        return self.novel_code == other.novel_code
    
    def __ne__(self, other):
        """Return True if the two Novel objects are not equal.

        Parameters
        ----------
        other : Novel
            The other Novel object to compare.
        """

        if not isinstance(other, Novel):
            raise TypeError("Other object must be a Novel object")
        return self.novel_code != other.novel_code