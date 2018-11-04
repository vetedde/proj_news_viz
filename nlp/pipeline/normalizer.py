import pymorphy2
from nltk import WordNetLemmatizer
from pymystem3 import Mystem
morph = pymorphy2.MorphAnalyzer()


class Normalizer(object):

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
            lemmatized = lemmatize_pymorph(words)
        elif self.lemma == 'mystem':
            mystem = Mystem()
            lemmatized = mystem.lemmatize(words)

        if not return_tokenized:
            return ' '.join(lemmatized)
        else:
            return lemmatized

    def lemmatize_pymorph(words):
        '''
        [0] токенизация предложения
        [1] проверка есть ли в начале слова '-'
        [2] проверка на стоп-слова
        [3] проверка есть ли данное слово в кэше
        [4] лемматизация слова
        на выходе лист токенов
        '''

        words_lem = []
        for w in words:
            if w in self.cache:
                words_lem.append(self.cache[w])
            else:
                temp_cach = self.cache[w] = morph.parse(w)[0].normal_form
                words_lem.append(temp_cach)
        return words_lem
