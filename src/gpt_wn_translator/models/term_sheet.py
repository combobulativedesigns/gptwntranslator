import spacy
import re

from janome.tokenizer import Tokenizer

from src.gpt_wn_translator.models.term import Term

class TermSheet:
    def __init__(self, new_terms, old_terms="", prev_summary="", current_chunk="", current_translation=""):
        self.old_terms = dict()
        self.new_terms = dict()
        self.combined_terms = dict()
        self.prev_summary = prev_summary
        self.current_chunk = current_chunk
        self.current_translation = current_translation
        self.tokens = []

        self.parse_existing_term_list_str(old_terms)
        self.parse_term_list_str(new_terms)
        self.init_tokens()
        self.calc_dimensions()

    def init_tokens(self):
        tokenizer = Tokenizer()

        try:
            self.tokens = tokenizer.tokenize(self.current_chunk)
        except Exception as e:
            raise Exception(f"Error while tokenizing: {e}")
    
    def calc_dimensions(self):
        try:
            # Calculate dimensions
            self.calc_term_chunk_frequencies()
            self.calc_term_document_frequencies()
            self.calc_term_summary_consistency()
            self.calc_term_prev_chunk_frequencies()
            self.calc_term_context_relevance()
            self.calc_term_ner()
            self.calc_term_novelty()
        except Exception as e:
            raise Exception(f"Error calculating dimensions: {e}")

    def parse_term_list_str(self, term_list_str=""):
        lines = term_list_str.splitlines()

        # Parse the cheat sheet
        for line in lines:
            # Skip empty lines
            if line == "":
                continue

            # Split the line into the japanese term, romanization, and english term
            pattern_match = re.match(r'- ([^\)]+)\s\(([^\)]+)\s*\)\s-\s([^\(]+)(?:\s\(.*)*(?:$|\n)', line)
            if pattern_match:
                japanese_term, romaji, english_term = pattern_match.groups()
            else:
                continue

            # Add the term to the cheat sheet
            if japanese_term not in self.new_terms:
                self.new_terms[japanese_term] = Term(japanese_term, romaji, english_term, 0, 0, 0, 0, 0, 0, 0)

            # Add the term to the cheat sheet
            if japanese_term not in self.combined_terms:
                self.combined_terms[japanese_term] = Term(japanese_term, romaji, english_term, 0, 0, 0, 0, 0, 0, 0)
    
    def parse_existing_term_list_str(self, term_list_str=""):
        lines = term_list_str.splitlines()

        # Parse the cheat sheet
        for line in lines:
            # Skip empty lines
            if line == "":
                continue

            # Split the line into the japanese term, romanization, and english term
            pattern_match = re.match(r'- ([^\)]+)\s\(([^\)]+)\s*\)\s-\s([^\(]+)\s\((\d+),\s(\d+),\s(\d+),\s(\d+),\s(\d+),\s(\d+),\s(\d+)\).*(?:$|\n)', line)
            if pattern_match:
                japanese_term, romaji, english_term, chunk_frequency, document_frequency, summary_consistency, prev_chunk_frequency, context_relevance, ner, novelty = pattern_match.groups()
            else:
                continue
            
            # Add the term to the cheat sheet
            if japanese_term not in self.old_terms:
                self.old_terms[japanese_term] = Term(japanese_term, romaji, english_term, int(chunk_frequency), int(document_frequency), int(summary_consistency), int(prev_chunk_frequency), int(context_relevance), int(ner), int(novelty))
            
            # Add the term to the cheat sheet
            if japanese_term not in self.combined_terms:
                self.combined_terms[japanese_term] = Term(japanese_term, romaji, english_term, int(chunk_frequency), int(document_frequency), int(summary_consistency), int(prev_chunk_frequency), int(context_relevance), int(ner), int(novelty))

    def calc_term_chunk_frequencies(self):
        try: 
            # for token in self.tokens:
            #     if token.surface in self.new_terms.keys():
            #         self.combined_terms[token.surface].chunk_frequency += 1
            for term in self.combined_terms.values():
                self.combined_terms[term.jp_term].chunk_frequency = self.current_chunk.count(term.jp_term)
        except Exception as e:
            raise Exception(f"Error calculating term chunk frequencies: {e}")

    def calc_term_document_frequencies(self):
        try:    
            # for token in self.tokens:
            #     if token.surface in self.new_terms.keys():
            #         self.combined_terms[token.surface].document_frequency = self.old_terms[token.surface].document_frequency + self.new_terms[token.surface].chunk_frequency
            for term in self.combined_terms.values():
                if term.jp_term in self.old_terms.keys():
                    self.combined_terms[term.jp_term].document_frequency = self.old_terms[term.jp_term].document_frequency + term.chunk_frequency
                else:
                    self.combined_terms[term.jp_term].document_frequency = term.chunk_frequency
        except Exception as e:
            raise Exception(f"Error calculating term document frequencies: {e}")

    def calc_term_summary_consistency(self):
        try:
            # for token in self.tokens:
            #     if token.surface in self.combined_terms:
            #         if token.surface in self.prev_summary:
            #             self.combined_terms[token.surface].summary_consistency = 1
            #         else:
            #             self.combined_terms[token.surface].summary_consistency = 0
            for term in self.combined_terms.values():
                if term.en_term in self.prev_summary:
                    self.combined_terms[term.jp_term].summary_consistency = 1
                else:
                    self.combined_terms[term.jp_term].summary_consistency = 0
        except Exception as e:
            raise Exception(f"Error calculating term summary consistency: {e}")

    def calc_term_prev_chunk_frequencies(self):
        try:
            # for token in self.tokens:
            #     if token.surface in self.combined_terms:
            #         self.combined_terms[token.surface].prev_chunk_frequency = self.old_terms[token.surface].chunk_frequency
            for term in self.combined_terms.values():
                if term.jp_term in self.old_terms.keys():
                    self.combined_terms[term.jp_term].prev_chunk_frequency = self.old_terms[term.jp_term].chunk_frequency
                else:
                    self.combined_terms[term.jp_term].prev_chunk_frequency = 0
        except Exception as e:
            raise Exception(f"Error calculating term previous chunk frequencies: {e}")

    def calc_term_context_relevance(self, window_size=5):
        try:
            # token_surfaces = [token.surface for token in self.tokens]
            # num_tokens = len(token_surfaces)

            # for term in self.old_terms:
            #     jp_term = term
            #     indices = [i for i, x in enumerate(token_surfaces) if x == jp_term]

            #     for index in indices:
            #         start, end = max(0, index - window_size), min(num_tokens, index + window_size + 1)
            #         for i in range(start, end):
            #             if token_surfaces[i] != jp_term:
            #                 if token_surfaces[i] in self.combined_terms:
            #                     self.combined_terms[token_surfaces[i]].context_relevance += 1
            terms = self.combined_terms.values()
            num_terms = len(terms)

            for term in terms:
                jp_term = term.jp_term
                indices = [i for i, x in enumerate(self.current_chunk) if x == jp_term]

                for index in indices:
                    start, end = max(0, index - window_size), min(num_terms, index + window_size + 1)
                    for i in range(start, end):
                        if self.current_chunk[i] != jp_term:
                            if self.current_chunk[i] in self.combined_terms:
                                self.combined_terms[self.current_chunk[i]].context_relevance += 1
        except Exception as e:
            raise Exception(f"Error calculating term context relevance: {e}")

    def calc_term_ner(self):
        try:
            nlp = spacy.load("ja_core_news_sm")
            doc = nlp(self.current_chunk)
            for ent in doc.ents:
                if ent.text in self.combined_terms.keys():
                    self.combined_terms[ent.text].ner = 1

            nlp = spacy.load("en_core_web_sm")
            doc = nlp(self.current_translation)
            for term in self.combined_terms.values():
                for ent in doc.ents:
                    if term.en_term == ent.text:
                        self.combined_terms[term.jp_term].ner = 1
        except Exception as e:
            raise Exception(f"Error calculating term NER: {e}")

    def calc_term_novelty(self):
        try:
            # for term in self.combined_terms:
            #     old_document_frequency = self.old_terms[term].document_frequency if term in self.old_terms else 0
            #     new_document_frequency = self.new_terms[term].document_frequency if term in self.new_terms else 0
            #     self.combined_terms[term].novelty = new_document_frequency - old_document_frequency
            for term in self.combined_terms.values():
                old_document_frequency = self.old_terms[term.jp_term].document_frequency if term.jp_term in self.old_terms else 0
                new_document_frequency = term.document_frequency
                self.combined_terms[term.jp_term].novelty = new_document_frequency - old_document_frequency
        except Exception as e:
            raise Exception(f"Error calculating term novelty: {e}")

    def get_top_terms(self, num_terms=15):
        if self.combined_terms:
            if len(self.combined_terms) > num_terms:
                return sorted(self.combined_terms.values(), reverse=True)[:num_terms]
            else:
                return sorted(self.combined_terms.values(), reverse=True)
        else:
            return []
    
    def __str__(self):
        terms_str = ""
        top_terms = self.get_top_terms()
        
        for term in top_terms:
            terms_str += f"{term.__str__()}\n"

        return terms_str
    
    def for_api(self):
        terms = ""
        top_terms = self.get_top_terms()
        
        for term in top_terms:
            terms += f"{term.en_term}\n"

        return terms


