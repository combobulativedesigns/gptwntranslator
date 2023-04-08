"""Term model."""

import copy


class Term:
    """This class represents a term."""

    def __init__(self, original_term, pho_rom_term, document_frequency: int=0, context_relevance: int=0, ner: int=0, translations: dict[str, str]=dict()) -> None:
        """Initialize the term.

        Parameters
        ----------
        original_term : str
            The original term.
        pho_rom_term : str
            The phonetic romanization of the original term.
        document_frequency : int
            The document frequency of the term.
        context_relevance : int
            The context relevance of the term.
        ner : int
            The NER (named entity recognition) value of the term.
        """

        # Validate parameters
        if not isinstance(original_term, str):
            raise TypeError("Original term must be a string")
        if not isinstance(pho_rom_term, str):
            raise TypeError("Phonetic romanization term must be a string")
        if not isinstance(document_frequency, int):
            raise TypeError("Document frequency must be an integer")
        if not isinstance(context_relevance, int):
            raise TypeError("Context relevance must be an integer")
        if not isinstance(ner, int):
            raise TypeError("NER value must be an integer")
        
        # Set the properties
        self.original_term = original_term
        self.pho_rom_term = pho_rom_term
        self.document_frequency = document_frequency
        self.context_relevance = context_relevance
        self.ner = ner
        self.translations = translations

    def __deepcopy__(self, memo) -> "Term":
        """Deep copy the term.

        Parameters
        ----------
        memo : dict
            The memo.

        Returns
        -------
        Term
            The deep copy of the term.
        """

        # Create a deep copy of the term
        copy_term = Term(
            self.original_term, 
            self.pho_rom_term, 
            document_frequency=self.document_frequency, 
            context_relevance=self.context_relevance, 
            ner=self.ner, 
            translations=copy.deepcopy(self.translations, memo))

        return copy_term

    def add_translation(self, language: str, translation: str):
        """Add a translation to the term.

        Parameters
        ----------
        language : str
            The language of the translation.
        translation : str
            The translation.
        """

        # Validate parameters
        if not isinstance(language, str):
            raise TypeError("Language must be a string")
        if not isinstance(translation, str):
            raise TypeError("Translation must be a string")
        
        # Add the translation
        self.translations[language] = translation

    def _get_weight(self) -> int:
        """Get the weight of the term.
        
        Returns
        -------
        int
            The weight of the term. Calculated as a weighted sum of the document frequency, context relevance and NER value.
        """

        # Define weights for each property
        w_document_frequency = 1
        w_context_relevance = 2
        w_ner = 3

        # Calculate the overall weight as a weighted sum
        weight = (self.document_frequency * w_document_frequency +
                self.context_relevance * w_context_relevance +
                self.ner * w_ner)

        return weight
    
    def has_translation(self, target_language: str) -> bool:
        """Check if the term has a translation for the target language.

        Parameters
        ----------
        target_language : str
            The target language of the translation.

        Returns
        -------
        bool
            True if the term has a translation for the target language, False otherwise.
        """

        # Validate the parameter
        if not isinstance(target_language, str):
            raise TypeError("Target language must be a string")
        
        # Check if the translation exists
        return target_language in self.translations
    
    def for_api(self, target_language: str) -> str:
        """Get the term for the API.

        Parameters
        ----------
        target_language : str
            The target language of the translation.

        Returns
        -------
        str
            The term for the API.
        """

        # Validate the parameter
        if not isinstance(target_language, str):
            raise TypeError("Target language must be a string")
        if target_language not in self.translations:
            raise ValueError("The target language is not available")
        
        # Get the translation
        translation = self.translations[target_language]

        return f"- {self.original_term} ({self.pho_rom_term}) - {translation}"
    
    def __str__(self):
        """Return the string representation of a Term object."""
        return f"- {self.original_term} ({self.pho_rom_term}) - ({self.document_frequency}, {self.context_relevance}, {self.ner})"
    
    def __eq__(self, other):
        """Return True if the two Term objects are equal.
        
        Parameters
        ----------
        other : Term
            The other Term object.

        Returns
        -------
        bool
            True if the two Term objects are equal, False otherwise.
        """

        # Validate the parameter
        if not isinstance(other, Term):
            raise TypeError("The other object must be a Term object")
        
        return self.original_term == other.original_term
    
    def __lt__(self, other):
        """Return True if the weight of the current Term object is less than the weight of the other Term object.

        Parameters
        ----------
        other : Term
            The other Term object.

        Returns
        -------
        bool
            True if the weight of the current Term object is less than the weight of the other Term object, False otherwise.
        """

        # Validate the parameter
        if not isinstance(other, Term):
            raise TypeError("The other object must be a Term object")
        
        return self._get_weight() < other._get_weight()
    
    def __gt__(self, other):
        """Return True if the weight of the current Term object is greater than the weight of the other Term object.

        Parameters
        ----------
        other : Term
            The other Term object.

        Returns
        -------
        bool
            True if the weight of the current Term object is greater than the weight of the other Term object, False otherwise.
        """

        # Validate the parameter
        if not isinstance(other, Term):
            raise TypeError("The other object must be a Term object")

        return self._get_weight() > other._get_weight()
    
    def __le__(self, other):
        """Return True if the weight of the current Term object is less than or equal to the weight of the other Term object.

        Parameters
        ----------
        other : Term
            The other Term object.

        Returns
        -------
        bool
            True if the weight of the current Term object is less than or equal to the weight of the other Term object, False otherwise.
        """

        # Validate the parameter
        if not isinstance(other, Term):
            raise TypeError("The other object must be a Term object")

        return self._get_weight() <= other._get_weight()
    
    def __ge__(self, other):
        """Return True if the weight of the current Term object is greater than or equal to the weight of the other Term object.

        Parameters
        ----------
        other : Term
            The other Term object.

        Returns
        -------
        bool
            True if the weight of the current Term object is greater than or equal to the weight of the other Term object, False otherwise.
        """

        # Validate the parameter
        if not isinstance(other, Term):
            raise TypeError("The other object must be a Term object")
        
        return self._get_weight() >= other._get_weight()
    
    def __ne__(self, other):
        """Return True if the two Term objects are not equal.

        Parameters
        ----------
        other : Term
            The other Term object.

        Returns
        -------
        bool
            True if the two Term objects are not equal, False otherwise.
        """

        # Validate the parameter
        if not isinstance(other, Term):
            raise TypeError("The other object must be a Term object")
        
        return self.original_term != other.original_term
