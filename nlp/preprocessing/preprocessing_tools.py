# coding: utf-8
import re
from nltk.corpus import stopwords
#pip install razdel
from razdel import tokenize # https://github.com/natasha/razdel
#pip install pymorphy2
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

stopword_ru = stopwords.words('russian')
with open('stopwords.txt', 'r', encoding='utf-8') as f:
    for w in f.readlines():
        stopword_ru.append(w)

cache = {}  # для кеша лемм


def clean_text(text):
    '''
    очистка текста
        
    на выходе очищеный текст
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
    лемматизация
        [0] если зашел тип не `str` делаем его `str`
        [1] токенизация предложения через razdel
        [2] проверка есть ли в начале слова '-'
        [3] проверка на стоп-слова
        [4] проверка токена с одного символа
        [5] проверка есть ли данное слово в кэше
        [6] лемматизация слова
        
        на выходе лист отлемматизированых токенов
    '''
    
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
