import json
from src.gpt_wn_translator.models.chapter import Chapter
from src.gpt_wn_translator.models.chunk import Chunk
from src.gpt_wn_translator.models.novel import Novel
from src.gpt_wn_translator.models.sub_chapter import SubChapter
from src.gpt_wn_translator.models.term import Term
from src.gpt_wn_translator.models.term_sheet import TermSheet

class JsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Term):
            return {
                "jp_term": o.jp_term,
                "ro_term": o.ro_term,
                "en_term": o.en_term,
                "chunk_frequency": o.chunk_frequency,
                "document_frequency": o.document_frequency,
                "summary_consistency": o.summary_consistency,
                "prev_chunk_frequency": o.prev_chunk_frequency,
                "context_relevance": o.context_relevance,
                "ner": o.ner,
                "term_novelty": o.term_novelty,
                "_type": "Term"
            }
        
        if isinstance(o, TermSheet):
            return {
                "old_terms": o.old_terms,
                "new_terms": o.new_terms,
                "combined_terms": o.combined_terms,
                "prev_summary": o.prev_summary,
                "current_chunk": o.current_chunk,
                "tokens": o.tokens,
                "_type": "TermSheet"
            }
        
        if isinstance(o, Chunk):
            return {
                "chunk_index": o.chunk_index,
                "chapter_index": o.chapter_index,
                "sub_chapter_index": o.sub_chapter_index,
                "contents": o.contents,
                "term_sheet": o.term_sheet,
                "summary": o.summary,
                "translation": o.translation,
                "translation_fixed": o.translation_fixed,
                "_type": "Chunk"
            }
        
        if isinstance(o, SubChapter):
            return {
                "sub_chapter_index": o.sub_chapter_index,
                "chapter_index": o.chapter_index,
                "name": o.name,
                "translated_name": o.translated_name,
                "link": o.link,
                "release_date": o.release_date,
                "contents": o.contents,
                "translation": o.translation,
                "summary": o.summary,
                "_type": "SubChapter"
            }
        
        if isinstance(o, Chapter):
            return {
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
                "title_translation": o.title_translation,
                "author": o.author,
                "author_translation": o.author_translation,
                "author_link": o.author_link,
                "description": o.description,
                "description_translation": o.description_translation,
                "chapters": o.chapters,
                "_type": "Novel"
            }

        return super(JsonEncoder, self).default(o)