"""Module containing classes for encoding objects to JSON format."""

import json
from gptwntranslator.models.chapter import Chapter
from gptwntranslator.models.chunk import Chunk
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.sub_chapter import SubChapter
from gptwntranslator.models.term import Term
from gptwntranslator.models.term_sheet import TermSheet


class JsonEncoder(json.JSONEncoder):
    """This class is used to encode objects to JSON format."""

    def default(self, o: object) -> dict:
        """This function is used to encode objects to JSON format.

        Parameters
        ----------
        o : object
            The object to encode.

        Returns
        -------
        dict
            The encoded object.
        """

        if isinstance(o, Term):
            return {
                "jp_term": o.jp_term,
                "ro_term": o.ro_term,
                "en_term": o.en_term,
                "document_frequency": o.document_frequency,
                "context_relevance": o.context_relevance,
                "ner": o.ner,
                "_type": "Term"
            }
        
        if isinstance(o, TermSheet):
            return {
                "novel_code": o.novel_code,
                "terms": o.terms,
                "_type": "TermSheet"
            }
        
        if isinstance(o, Chunk):
            return {
                "novel_code": o.novel_code,
                "chapter_index": o.chapter_index,
                "sub_chapter_index": o.sub_chapter_index,
                "chunk_index": o.chunk_index,
                "contents": o.contents,
                "prev_line": o.prev_line,
                "next_line": o.next_line,
                "translation": o.translation,
                "_type": "Chunk"
            }
        
        if isinstance(o, SubChapter):
            return {
                "novel_code": o.novel_code,
                "chapter_index": o.chapter_index,
                "sub_chapter_index": o.sub_chapter_index,
                "link": o.link,
                "name": o.name,
                "contents": o.contents,
                "release_date": o.release_date,
                "translated_name": o.translated_name,
                "translation": o.translation,
                "summary": o.summary,
                "_type": "SubChapter"
            }
        
        if isinstance(o, Chapter):
            return {
                "novel_code": o.novel_code,
                "chapter_index": o.chapter_index,
                "name": o.name,
                "translated_name": o.translated_name,
                "sub_chapters": o.sub_chapters,
                "_type": "Chapter"
            }
        
        if isinstance(o, Novel):
            return {
                "novel_code": o.novel_code,
                "title": o.title,
                "author": o.author,
                "description": o.description,
                "title_translation": o.title_translation,
                "author_translation": o.author_translation,
                "author_link": o.author_link,
                "description_translation": o.description_translation,
                "chapters": o.chapters,
                "terms_sheet": o.terms_sheet,
                "_type": "Novel"
            }

        return super(JsonEncoder, self).default(o)