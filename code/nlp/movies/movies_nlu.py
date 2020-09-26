"""
Simple NLU for the movie domain
===============================

Author: Shuo Zhang, Krisztian Balog
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# from code.nlp.movies import *
from nltk.tokenize import word_tokenize
from code.nlp.nlu import NLU
import pandas as pd
import re

PRE_FILE = "code/data/metadata_prep.csv"


class MoviesNLU(NLU):
    """Movies NLU"""
    def __init__(self):
        super(NLU, self).__init__()
        self.metadata, self.titles_all, self.tfidf_fit_nlu, \
        self.tfidf_matrix_nlu = self.naive_index()

    def naive_index(self):
        """Loads MovieLens dataset as local index."""
        metadata = pd.read_csv(PRE_FILE)  # cf. user/ml-20m/data_pre for data preparation
        titles = metadata['title'].tolist()
        docs = [self.text_prepare(title) for title in titles if isinstance(title, str)]
        titles_all = [title for title in titles if isinstance(title, str)]
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_fit = tfidf_vectorizer.fit(docs)
        tfidf_matrix = tfidf_fit.transform(docs)
        return metadata, titles_all, tfidf_fit, tfidf_matrix

    @staticmethod
    def text_prepare(doc):
        doc = doc.lower()
        doc = REPLACE_BY_SPACE_RE.sub(' ', doc)
        doc = BAD_SYMBOLS_RE.sub('', doc)
        doc = " ".join([w for w in word_tokenize(doc)])
        return doc

    @staticmethod
    def parse(text):
        """Removes special tags to avoid problems such as parenthesis matching in regex."""
        for tag in ["\n", ";)"]:
            while tag in text:
                text = text.replace(tag, "")
        return text

    def find_pattern(self, utterance):
        """Finds the pattern by checking the prefix, i.e., checking the terms by splitting."""
        prefix_list = UTTERANCE_PATTERN
        for i in range(len(utterance.split())):
            # Extend prefix by pointing the next term, and keep utterances having the same prefix
            current_prefix_list = [j for j in prefix_list if utterance.split()[i] == j.split()[i]]
            prefix_list = current_prefix_list
            if len(prefix_list) == 1:
                return UTTERANCE_PATTERN.get(prefix_list[0])
        print("AGENT: ", utterance)
        raise SyntaxError("Pattern not found!")

    def link_entity(self, sf, id=None):
        """Links entity for the given surface form"""
        a = list(cosine_similarity(self.tfidf_fit_nlu.transform([self.text_prepare(sf)]),
                                   self.tfidf_matrix_nlu.tocsr())[0])
        b = sorted(range(len(a)), key=lambda i: a[i], reverse=True)[:1][0]
        return self.titles_all[b] if not id else b  # return title or id

    def link_entities(self, text):
        """Links entities in the given text."""
        sfs = self.extract_sf(self.parse(text))
        return [(text, sf, self.link_entity(sf), self.movie_genre(sf)) for sf in sfs]

    def extract_sf(self, text):
        """Based on the recorded utterance patterns
        (cf. UTTERANCE_PATTERN), locate and extract
        surface forms for movie titles"""
        pattern = self.find_pattern(utterance=text)
        p = re.compile(pattern).findall(text)
        return p if isinstance(p[0], str) else list(p[0])

    def movie_genre(self, title):
        """Finds movie genre based on movie title."""
        try:
            res = str(self.metadata[self.metadata['title'] == title]
                      ['genres'].values[0]).split(", ")
        except Exception:
            res = []
        return res
