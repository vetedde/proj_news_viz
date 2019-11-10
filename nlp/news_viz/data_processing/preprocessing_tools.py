import html
import re

import pymorphy2  # pip install pymorphy2

morph = pymorphy2.MorphAnalyzer()

import os
import sys

PATH = os.path.join(os.getenv('HOME'), 'proj_news_radar/proj_news_viz/nlp')
sys.path.append(PATH)

# read stopwords for RU
try:
    with open(f'{PATH}/data/another/stopwords.txt', "r") as file:
        stopwords = file.read().splitlines()
except FileNotFoundError:
    stopwords = []


def clean_text(text: str = None) -> str:
    '''
    clean text, leaving only tokens for clustering
    
    Parameters
    ----------
    text : string, default None
        input text 
        
    Returns
    -------
    text : string
        cleaned string text
    '''

    if not isinstance(text, str):
        text = str(text)

    text = html.unescape(text)

    text = text.lower()
    text = re.sub(r'[^а-яА-Я\-]+', ' ', text)  # leave the Cyrillic alphabet
    text = re.sub(r'(?<!\S).(?!\S)\s*', '', text)  # remove the single characters
    text = re.sub(r'\s+', ' ', text).strip()  # remove the long blanks

    if len(text) < 3:
        return '9999'
    else:
        return text


def lemmatization(text: str = None) -> str:
    '''
    lemmatization text 
    
    Parameters
    ----------
    input_text : string, default None
        cleaned text
        
    Returns
    -------
    words_lem : string
        lemmatized text
    '''

    # get tokens from input text
    # in this case it's normal approach because we hard cleaned text
    if not isinstance(text, str):
        text = str(text)

    # get tokens from input text
    # in this case it's normal approach because we hard cleaned text
    tokens = text.split(' ')

    words_lem = [morph.parse(token)[0].normal_form for token in tokens if token not in stopwords]

    if len(words_lem) < 3:
        return '9999'
    else:
        return ' '.join(words_lem)
