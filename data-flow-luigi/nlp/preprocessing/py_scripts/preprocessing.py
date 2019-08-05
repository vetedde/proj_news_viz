# -*- coding: utf-8 -*-

import os
import sys
import re
import pymorphy2

from pymystem3 import Mystem
from nltk.corpus import stopwords
from razdel import tokenize

cache = dict()
stopword_ru = stopwords.words('russian')
morph = pymorphy2.MorphAnalyzer()
mystem = Mystem()

def clean_text(text):
    '''
    Cleans text.
    '''
   
    if not isinstance(text, str):
        text = str(text)
    
    text = text.lower()
    text = text.strip('\n').strip('\r').strip('\t')

    text = re.sub("-\s\r\n\|-\s\r\n|\r\n", '', str(text))

    text = re.sub("[0-9]|[-—.,:;_%©«»?*!@#№$^•·&()]|[+=]|[[]|[]]|[/]|", '', text)
    text = re.sub(r"\r\n\t|\n|\\s|\r\t|\\n", ' ', text)
    text = re.sub(r'[\xad]|[\s+]', ' ', text.strip())

    return text

def lemmatization(text):
    '''
    Lemmatizes a text:
        [0] - if the type!="str" - make it ""str
        [1] - tokenizes text
        [2] - removes words with the first letter=="-"
        [3] - removes stopwords
        [4] - removes words with len<=1
        [5] - trying to find a word in cache
        [6] - lemmatizes words
    Output: lemmatized text
    '''
    global cache
    # [0]
    if not isinstance(text, str):
        text = str(text)
    
    # [1]
    tokens = list(tokenize(text))
    words = [_.text for _ in tokens]

    
    words_lem = []
    for w in words:
        if w[0] == '-': # [2]
            w = w[1:]
        if not w in stopword_ru: # [3]
            if len(w)>1: # [4]
                if w in cache: # [5]
                    words_lem.append(cache[w])
                else: # [6]
                    temp_cach = cache[w] = morph.parse(w)[0].normal_form
                    words_lem.append(temp_cach)
    return words_lem


def lemmatization_mystem(text):
    if not isinstance(text, str):
        text = str(text)
    
    lemmas = mystem.lemmatize(text)
    
    return [word for word in lemmas if len(word)>1]






