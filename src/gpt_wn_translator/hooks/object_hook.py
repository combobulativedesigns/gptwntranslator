from src.gpt_wn_translator.models.chapter import Chapter
from src.gpt_wn_translator.models.chunk import Chunk
from src.gpt_wn_translator.models.novel import Novel
from src.gpt_wn_translator.models.sub_chapter import SubChapter
from src.gpt_wn_translator.models.term import Term
from src.gpt_wn_translator.models.term_sheet import TermSheet


def generic_object_hook(dct):
    if '_type' in dct:
        if dct['_type'] == 'Novel':
            return Novel(
                dct['novel_code'], 
                dct['title'], 
                dct['title_translation'], 
                dct['author'], 
                dct['author_translation'], 
                dct['author_link'], 
                dct['description'], 
                dct['description_translation'], 
                dct['chapters'])
        
        elif dct['_type'] == 'Chapter':
            return Chapter(
                dct['chapter_index'], 
                dct['name'], 
                dct['translated_name'], 
                dct['sub_chapters'])
        
        elif dct['_type'] == 'SubChapter':
            return SubChapter(
                dct['sub_chapter_index'], 
                dct['chapter_index'], 
                dct['name'], 
                dct['translated_name'], 
                dct['link'], 
                dct['release_date'], 
                dct['contents'], 
                dct['translation'], 
                dct['summary'])
        
        elif dct['_type'] == 'Chunk':
            return Chunk(
                dct['chunk_index'], 
                dct['chapter_index'], 
                dct['sub_chapter_index'], 
                dct['contents'], 
                dct['term_sheet'], 
                dct['summary'], 
                dct['translation'], 
                dct['translation_fixed'])
        
        elif dct['_type'] == 'TermSheet':
            return TermSheet(
                dct['old_terms'], 
                dct['new_terms'], 
                dct['combined_terms'], 
                dct['prev_summary'], 
                dct['current_chunk'], 
                dct['tokens'])
        
        elif dct['_type'] == 'Term':
            return Term(
                dct['jp_term'], 
                dct['ro_term'], 
                dct['en_term'], 
                dct['chunk_frequency'],
                dct['document_frequency'],
                dct['summary_consistency'],
                dct['prev_chunk_frequency'],
                dct['context_relevance'],
                dct['ner'],
                dct['term_novelty'])
        
    return dct
