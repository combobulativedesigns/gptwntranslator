class Term:
    def __init__(self, jp_term, ro_term, en_term, chunk_frequency, document_frequency, summary_consistency, prev_chunk_frequency, context_relevance, ner, term_novelty):
        self.jp_term = jp_term
        self.ro_term = ro_term
        self.en_term = en_term
        self.chunk_frequency = chunk_frequency
        self.document_frequency = document_frequency
        self.summary_consistency = summary_consistency
        self.prev_chunk_frequency = prev_chunk_frequency
        self.context_relevance = context_relevance
        self.ner = ner
        self.term_novelty = term_novelty

    def get_weight(self):
        # Define weights for each property
        w_chunk_frequency = 1
        w_document_frequency = 1
        w_summary_consistency = 2
        w_prev_chunk_frequency = -1
        w_context_relevance = 1
        w_ner = 3
        w_term_novelty = -1

        # Calculate the overall weight as a weighted sum
        weight = (self.chunk_frequency * w_chunk_frequency +
                self.document_frequency * w_document_frequency +
                self.summary_consistency * w_summary_consistency +
                self.prev_chunk_frequency * w_prev_chunk_frequency +
                self.context_relevance * w_context_relevance +
                self.ner * w_ner +
                self.term_novelty * w_term_novelty)

        return weight
    
    def for_api(self):
        return f"- {self.jp_term} ({self.ro_term}) - {self.en_term}"
    
    def __str__(self):
        return f"- {self.jp_term} ({self.ro_term}) - {self.en_term} ({self.chunk_frequency}, {self.document_frequency}, {self.summary_consistency}, {self.prev_chunk_frequency}, {self.context_relevance}, {self.ner}, {self.term_novelty})"
    
    def __eq__(self, other):
        return self.jp_term == other.jp_term
    
    def __hash__(self):
        return hash(self.jp_term)
    
    def __lt__(self, other):
        return self.get_weight() < other.get_weight()
    
    def __gt__(self, other):
        return self.get_weight() > other.get_weight()
    
    def __le__(self, other):
        return self.get_weight() <= other.get_weight()
    
    def __ge__(self, other):
        return self.get_weight() >= other.get_weight()
    
    def __ne__(self, other):
        return self.jp_term != other.jp_term
