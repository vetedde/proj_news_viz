# coding: utf-8
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pymorphy2  # pip install pymorphy2
morph = pymorphy2.MorphAnalyzer()

stopword_ru = stopwords.words('russian')
stopword_ru.append('м')
stopword_ru.append('это')
stopword_ru.append('по')

cache = {}  # для кеша лемм


def clean_text(text):
    '''
        очистка текста от мусора

    '''

    text = re.sub('-\s\r\n\|-\s\r\n|\r\n|[«»]|[""]|[><]"[\[]]|//"', '', str(text))
    text = re.sub('[«»]|[""]|[><]"[\[]]"', '', text)
    text = re.sub('[0-9]|[-.,:;_%©?*!@#№$^•·&()]|[+=]|[[]|[]]|[/]|"|–|—|', ' ', text)
    text = re.sub(r'\r\n\t|\n|\\s|\r\t|\\n', ' ', text)
    text = re.sub(r'[\xad]|[\s+]', ' ', text)
    text = re.sub('ё', 'е', text.strip().lower())

    return text


def token_stop_pymorph(text):
    '''
        [0] токенизация предложения
        [1] проверка есть ли в начале слова '-'
        [2] проверка на стоп-слова
        [3] проверка есть ли данное слово в кэше
        [4] лемматизация слова

    на выходе лист токенов
    '''

    words = word_tokenize(text)

    words_lem = []
    for w in words:
        if w[0] == '-':
            try:
                if not w[1:] in stopword_ru:
                    if w[1:] in cache:
                        print('enter')
                        words_lem.append(cache[w[1:]])
                    else:
                        temp_cach = cache[w[1:]] = morph.parse(w[1:])[
                            0].normal_form
                        words_lem.append(temp_cach)
            except:
                pass
        else:
            try:
                if not w in stopword_ru:
                    if w in cache:
                        words_lem.append(cache[w])
                    else:
                        temp_cach = cache[w] = morph.parse(w)[0].normal_form
                        words_lem.append(temp_cach)
            except:
                pass
    return words_lem
