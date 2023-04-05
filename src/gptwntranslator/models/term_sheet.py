"""Terms sheet model."""

from types import NoneType
import spacy
import re

from janome.tokenizer import Tokenizer
from gptwntranslator.helpers.config_helper import Config

from gptwntranslator.models.term import Term

class TermSheet:
    """This class represents a terms sheet."""

    def __init__(self, novel_code: str, terms: dict[str, Term]|NoneType=None) -> None:
        """Initialize a terms sheet object.

        Parameters
        ----------
        novel_code : str
            The code of the novel.
        terms : dict[str, Term]|NoneType, optional
            The terms in the terms sheet, by default None
        """

        # Validate parameters
        if not isinstance(novel_code, str):
            raise TypeError("Novel code must be a string")
        if not isinstance(terms, (NoneType, dict)):
            raise TypeError("Terms must be a dictionary of terms")
        
        # Initialize properties
        self.novel_code = novel_code
        self.terms = dict() if terms is None else terms

    def process_new_terms(self, term_list_str: str):
        """Parse a string of terms into a dictionary of terms.

        Parameters
        ----------
        term_list_str : str
            The string of terms to parse
        """

        # Validate parameters
        if not isinstance(term_list_str, str):
            raise TypeError("Term list string must be a string")
        
        # Initialize variables
        lines = term_list_str.splitlines()
        cf = Config()

        # Parse the cheat sheet
        for line in lines:
            # Skip empty lines
            if line == "":
                continue

            # Split the line into the original term, romanization/phonetic, and translated term
            pattern_match = re.match(r'- ([^\)]+)\s\(([^\)]+)\s*\)\s-\s([^\(]+)(?:\s\(.*)*(?:$|\n)', line)
            if pattern_match:
                original_term, ro_pho_term, translated_term = pattern_match.groups()
            else:
                continue

            # Add the term to the list of terms
            if original_term not in self.terms:
                self.terms[original_term] = Term(original_term, ro_pho_term)

            # Add the translation to the term
            language = cf.data.config.translator.target_language
            if language not in self.terms[original_term].translations:
                self.terms[original_term].add_translation(language, translated_term)

    def update_dimensions(self, novel_str: str, original_language: str) -> None:
        """Update the dimensions of the terms sheet.

        Parameters
        ----------
        novel_str : str
            The novel to update the dimensions for.
        """

        # Validate parameters
        if not isinstance(novel_str, str):
            raise TypeError("Novel string must be a string")

        # Calculate the term document frequencies
        self._calc_term_document_frequencies(novel_str)

        # Calculate the term context relevance
        self._calc_term_context_relevance(novel_str)

        # Calculate the terms NER value
        self._calc_term_ner(original_language)


    def _calc_term_document_frequencies(self, novel_str: str) -> None:
        """Calculate the document frequencies of the terms in the terms sheet.

        Parameters
        ----------
        novel_str : str
            The novel to calculate the document frequencies for.
        """

        # Validate parameters
        if not isinstance(novel_str, str):
            raise TypeError("Novel string must be a string")

        try: 
            for term in self.terms.values():
                self.terms[term.original_term].document_frequency += novel_str.count(term.original_term)
        except Exception as e:
            raise Exception(f"Error calculating term chunk frequencies: {e}")
        
    def _calc_term_context_relevance(self, novel_str: str, window_size: int=5) -> None:
        """Calculate the context relevance of the terms in the terms sheet.

        Parameters
        ----------
        novel_str : str
            The novel to calculate the context relevance for.
        window_size : int
            The size of the window to calculate the context relevance for, defaults to 5.
        """

        # Validate parameters
        if not isinstance(novel_str, str):
            raise TypeError("Novel string must be a string")
        if not isinstance(window_size, int):
            raise TypeError("Window size must be an integer")

        try:
            # Get the terms and the number of terms
            terms = self.terms.values()
            num_terms = len(terms)

            # Calculate the context relevance for each term
            for term in terms:
                original_term = term.original_term
                indices = [i for i, x in enumerate(novel_str) if x == original_term]

                for index in indices:
                    start, end = max(0, index - window_size), min(num_terms, index + window_size + 1)
                    for i in range(start, end):
                        if novel_str[i] != original_term:
                            if novel_str[i] in self.terms:
                                self.terms[novel_str[i]].context_relevance += 1
        except Exception as e:
            raise Exception(f"Error calculating term context relevance: {e}")

    def _calc_term_ner(self, original_language: str) -> None:
        """Find terms which are named entities in the novel.

        Parameters
        ----------
        novel_str : str
            The novel to find named entities in.
        """

        cf = Config()
        pipeline = cf.get_spacy_pipeline_for_language_code(original_language)

        try:
            # Load the spacy model
            nlp = spacy.load(pipeline)
            
            for term in self.terms.values():
                doc = nlp(term.original_term)

                for ent in doc.ents:
                    if ent.text == term.original_term:
                        term.ner = 1
                        break
        except Exception as e:
            raise Exception(f"Error calculating term NER: {e}")

    def _get_top_terms(self, chunk: str|NoneType=None, num_terms: int=15) -> list[Term]:
        """Get the top terms from the terms sheet.

        Parameters
        ----------
        chunk : str|NoneType, optional
            The chunk to get the top terms for. If None, get the top terms for the entire novel. By default None
        num_terms : int, optional
            The number of terms to get, by default 15
        
        Returns
        -------
        list[Term]
            The top terms.
        """

        # Validate parameters
        if chunk is not None and not isinstance(chunk, str):
            raise TypeError("Chunk must be a string")
        if not isinstance(num_terms, int):
            raise TypeError("Number of terms must be an integer")
        
        # Get the top terms
        if self.terms:
            # If there are terms
            if len(self.terms) > num_terms:
                # If there are more terms than the number of terms to get
                if chunk is None:
                    # If the chunk is None, get the top terms from the entire novel, capped at the number of terms
                    terms = sorted(self.terms.values(), reverse=True)[:num_terms]
                else:
                    # If the chunk is not None, get the top terms from the chunk, capped at the number of terms
                    terms = sorted([term for term in self.terms.values() if term.original_term in chunk], reverse=True)[:num_terms]
            else:
                # If there are less terms than the number of terms to get
                if chunk is None:
                    # If the chunk is None, get the top terms from the entire novel
                    terms = sorted(self.terms.values(), reverse=True)
                else:
                    # If the chunk is not None, get the top terms from the chunk
                    terms = sorted([term for term in self.terms.values() if term.original_term in chunk], reverse=True)
        else:
            # If there are no terms, return an empty list
            terms = []

        return terms
    
    def __str__(self):
        """Get the string representation of the terms sheet."""

        # Get the top terms
        terms_str = ""
        top_terms = self._get_top_terms()
        
        # Get the string representation of the top terms
        for term in top_terms:
            terms_str += f"{term.__str__()}\n"

        return terms_str
    
    def for_api(self, chunk: str, target_language: str, num_terms: int=15) -> str:
        """Get the string representation of the terms sheet for the API.

        Parameters
        ----------
        chunk : str
            The chunk to get the top terms for.
        target_language : str
            The target language of the translation.
        num_terms : int, optional
            The number of terms to get, by default 15

        Returns
        -------
        str
            The string representation of the terms sheet for the API.
        """

        # Validate parameters
        if not isinstance(chunk, str):
            raise TypeError("Chunk must be a string")
        if not isinstance(target_language, str):
            raise TypeError("Target language must be a string")
        if not isinstance(num_terms, int):
            raise TypeError("Number of terms must be an integer")
        
        # Get the top terms
        terms = ""
        top_terms = self._get_top_terms()
        
        # Get the string representation of the top terms
        for term in [term for term in top_terms if term.has_translation(target_language)]:
            terms += f"{term.for_api(target_language)}\n"

        return terms


