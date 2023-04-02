"""This module contains the object hook for the JSON decoder."""

from gptwntranslator.models.chapter import Chapter
from gptwntranslator.models.chunk import Chunk
from gptwntranslator.models.novel import Novel
from gptwntranslator.models.sub_chapter import SubChapter
from gptwntranslator.models.term import Term
from gptwntranslator.models.term_sheet import TermSheet


def generic_object_hook(dct: dict):
    """This function is used to decode JSON objects into Python objects.
    
    Parameters
    ----------
    dct : dict
        The dictionary to decode.
    """

    # Validate parameters
    if not isinstance(dct, dict):
        raise TypeError("Dictionary must be a dictionary")
    
    if '_type' in dct:
        if dct['_type'] == 'Novel':
            return Novel(
                dct['novel_code'], 
                dct['title'], 
                dct['author'], 
                dct['description'], 
                title_translation=dct['title_translation'], 
                author_translation=dct['author_translation'], 
                author_link=dct['author_link'], 
                description_translation=dct['description_translation'], 
                chapters=dct['chapters'], 
                terms_sheet=dct['terms_sheet'])
        
        elif dct['_type'] == 'Chapter':
            return Chapter(
                dct['novel_code'], 
                dct['chapter_index'], 
                dct['name'], 
                translated_name=dct['translated_name'], 
                sub_chapters=dct['sub_chapters'])
        
        elif dct['_type'] == 'SubChapter':
            return SubChapter(
                dct['novel_code'], 
                dct['chapter_index'], 
                dct['sub_chapter_index'], 
                dct['link'], 
                dct['name'], 
                dct['contents'], 
                dct['release_date'], 
                translated_name=dct['translated_name'], 
                translation=dct['translation'], 
                summary=dct['summary'])
        
        elif dct['_type'] == 'Chunk':
            return Chunk(
                dct['novel_code'],
                dct['chapter_index'], 
                dct['sub_chapter_index'], 
                dct['chunk_index'], 
                dct['contents'], 
                dct['prev_line'], 
                dct['next_line'], 
                translation=dct['translation']) 
        
        elif dct['_type'] == 'TermSheet':
            return TermSheet(
                dct['novel_code'], 
                terms=dct['terms']) 
        
        elif dct['_type'] == 'Term':
            return Term(
                dct['jp_term'], 
                dct['ro_term'], 
                dct['en_term'], 
                document_frequency=dct['document_frequency'],
                context_relevance=dct['context_relevance'],
                ner=dct['ner'])
        
    return dct
