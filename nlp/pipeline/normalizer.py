import pymorphy2
from nltk import WordNetLemmatizer
from pymystem3 import Mystem
morph = pymorphy2.MorphAnalyzer()


class Normalizer(object):
    """
    Class for normalizing text data.

    Currently supports nltk WordNetLemmatizer, pymorphy and mystem.

    """

    def __init__(self, lemma : str = 'nltk'):

        self.lemma = lemma
        self.cache = {}

    def normalize(self, text : list, simple_tokenize: bool = False, return_tokenized: bool = False):
        if simple_tokenize:
            words = text.split()
        else:
            words = text

        if self.lemma == 'nltk':
            lemmatizer = WordNetLemmatizer()
            lemmatized = [lemmatizer.lemmatize(w) for w in words]
        elif self.lemma == 'pymorphy':
            lemmatized = self.lemmatize_pymorph(words)
        elif self.lemma == 'mystem':
            mystem = Mystem()
            lemmatized = mystem.lemmatize(words)

        if not return_tokenized:
            return ' '.join(lemmatized)
        else:
            return lemmatized

    def lemmatize_pymorph(self, words):

        words_lem = []
        for w in words:
            if w in self.cache:
                words_lem.append(self.cache[w])
            else:
                temp_cach = self.cache[w] = morph.parse(w)[0].normal_form
                words_lem.append(temp_cach)
        return words_lem
