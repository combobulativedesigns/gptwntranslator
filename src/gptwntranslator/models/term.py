"""Term model."""

class Term:
    """This class represents a term."""

    def __init__(self, jp_term: str, ro_term: str, en_term: str, document_frequency: int=0, context_relevance: int=0, ner: int=0):
        """Initialize the term.

        Parameters
        ----------
        jp_term : str
            The Japanese term.
        ro_term : str
            The Romaji term.
        en_term : str
            The English term.
        document_frequency : int
            The document frequency of the term.
        context_relevance : int
            The context relevance of the term.
        ner : int
            The NER (named entity recognition) value of the term.
        """

        # Validate parameters
        if not isinstance(jp_term, str):
            raise TypeError("Japanese term must be a string")
        if not isinstance(ro_term, str):
            raise TypeError("Romaji term must be a string")
        if not isinstance(en_term, str):
            raise TypeError("English term must be a string")
        if not isinstance(document_frequency, int):
            raise TypeError("Document frequency must be an integer")
        if not isinstance(context_relevance, int):
            raise TypeError("Context relevance must be an integer")
        if not isinstance(ner, int):
            raise TypeError("NER value must be an integer")
        
        # Set the properties
        self.jp_term = jp_term
        self.ro_term = ro_term
        self.en_term = en_term
        self.document_frequency = document_frequency
        self.context_relevance = context_relevance
        self.ner = ner

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
    
    def for_api(self) -> str:
        """Get the term for the API.

        Returns
        -------
        str
            The term for the API.
        """

        return f"- {self.jp_term} ({self.ro_term}) - {self.en_term}"
    
    def __str__(self):
        """Return the string representation of a Term object."""
        return f"- {self.jp_term} ({self.ro_term}) - {self.en_term} ({self.document_frequency}, {self.context_relevance}, {self.ner})"
    
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
        
        return self.jp_term == other.jp_term
    
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
        
        return self.jp_term != other.jp_term
