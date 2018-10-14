# coding: utf-8
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

#pip install pymystem3
from pymystem3 import Mystem
#m=Mystem()

stopword_ru=stopwords.words('russian')
stopword_ru.append('м')
stopword_ru.append('это')
stopword_ru.append('по')

def clean_text(text):
    '''
    убираем с текста всякий мусор
    '''
    
    text = re.sub('-\s\r\n\s+|-\s\r\n|\r\n|[«»]|[><]', ' ', text.lower())    
    text = re.sub('[.,:;_%©?*!@#№$^•·&()]|[+=]|[[]|[]]|[/]|"|–|—|', ' ', text)
    text = re.sub('\’|\”|‘', ' ', text)
    text = re.sub(r'[\\n]|[\d]', '', text)
    text = re.sub(r'ё', 'е', text)
    
    return text

def lemma_by_mystem(text):
    '''
    [0] лемматизируем все предложение сразу с помощью pymystem3
    [1] токенизируем с помощью nltk.word_tokenize и убираем стоп-слова

    на выходе лист отлемматизированных токенов
    '''
    
    text_new=''.join(Mystem().lemmatize(text))
    
    words_new=[]
    for w in word_tokenize(text_new):
        #print(w)
        if w[0]=='-':
            try:
                if not w[1:] in stopword_ru:
                    words_new.append(w[1:])
            except:pass
        elif w[-1]=='-':
            try:
                if not w[:-1] in stopword_ru:
                    words_new.append(w[:-1])
            except:pass
        else:
            if not w in stopword_ru:
                words_new.append(w)
    
    return words_new

'''
def clean_text(text): 
    
    #убираем мусор
    text = nltk.re.sub('-\s\r\n\s+|-\s\r\n|\r\n|[«»]|[><]', ' ', text.lower())    
    text = nltk.re.sub('[0-9]|[.,:;_%©?*!@#№$^•·&()\d]|[+=]|[[]|[]]|[/]|"|\s{2,}|-|–|—|', ' ', text)
    text = re.sub(r"\d+", ' ', text, flags=re.UNICODE)
    text = re.sub('\’|\”|‘', ' ', text)
    text = re.sub(r'\\n', '', text)
    text = re.sub('ё', 'е', text)
    
    #убираем стоп-слова
    words = text.split()
    words = [w for w in words if not w in stopword_ru]
    
    #джойним слова
    return ' '.join(words)
'''