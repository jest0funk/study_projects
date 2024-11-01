class CountVectorizer:
    """In this class a corpus is considered as an iterable of sequences.
    Each sequence is considered as an iterable of tokens.
    In case of doubt, whether public or not, class attributes are made non-public by adding a leading underscore."""

    def __init__(self, ngram_size):
        """The magic __init___ method sets the ngram_size parameter input and sets it as a class attribute."""
        self._ngram_size = ngram_size

    def fit(self, corpus):
        """The method fit, at first, initializes a temporary set and fills it with tokens while iterating through corpus.
        Token iteration within a sequence of the corpus is performed by a separate static method.
        Then the method builds a token-to-index dictionary by converting the temporary set to a list, 
        sorting the list, and then enumerating it.
        The dictionary is saved as _vocabulary class attribute."""
        _tmp_vocabulary = set()
        for sequence in corpus:
            _tmp_vocabulary.update(
                {token for token in self._token_iterator(sequence, self._ngram_size)}
            )
        self._vocabulary = {
            token: key for key, token in enumerate(sorted(list(_tmp_vocabulary)))
        }

    def transform(self, corpus):
        """The method transform, at first, initializes a list which is intended to collect results of transformation 
        and which in the end is returned by the method.
        Then it iterates through corpus sequences and for each sequence initializes a dictionary of tokens with 0 values 
        through dict comprehension on the basis of _vocabulary class attribute.
        Next an iteration through sequence tokens with the use of static method is performed and, 
        if a token is in the sequence dictionary, its index reflects the count of its appearance in the sequence.
        After every such iteration through sequence tokens the values of the sequence dictionary are appended 
        as a list to the result collecting list.
        This processing is performed for each sequence of the corpus, 
        then the result collecting list is returned by the method."""
        _transformed_corpus = list()
        for sequence in corpus:
            _sequence_vocabulary = {token: 0 for token in self._vocabulary.keys()}
            for token in self._token_iterator(sequence, self._ngram_size):
                if token in self._vocabulary.keys():
                    _sequence_vocabulary[token] += 1
            _transformed_corpus.append(list(_sequence_vocabulary.values()))
        return _transformed_corpus

    def fit_transform(self, corpus):
        """The fit_transform method simply calls the two methods performing fit and transform proceedings 
        of the same corpus."""
        self.fit(corpus)
        return self.transform(corpus)

    @staticmethod
    def _token_iterator(iteration_sequence, iteration_ngram_size):
        """In order to avoid repeated code of token iteration this procedure was moved to a separate static method."""
        for n in range(len(iteration_sequence) - iteration_ngram_size + 1):
            yield iteration_sequence[n : iteration_ngram_size + n]
