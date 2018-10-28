import re
from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem.wordnet import WordNetLemmatizer
# import pymorphy2  # pip install pymorphy2
# morph = pymorphy2.MorphAnalyzer()


def clean_text(text, russian_words_only: bool, remove_stop: bool = True):

    text = text.lower()
    if russian_words_only:
        text = re.sub("[^а-я]", ' ', text)
        text = text.strip()

    else:
        text = re.sub('-\s\r\n\|-\s\r\n|\r\n|[«»]|[""]|[><]"[\[]]|//"', '', text)
        text = re.sub('[«»]|[""]|[><]"[\[]]"', '', text)
        text = re.sub('[0-9]|[-.,:;_%©?*!@#№$^•·&()]|[+=]|[[]|[]]|[/]|"|–|—|', ' ', text)
        text = re.sub(r'\r\n\t|\n|\\s|\r\t|\\n', ' ', text)
        text = re.sub(r'[\xad]|[\s+]', ' ', text)
        text = re.sub('ё', 'е', text.strip())

    if remove_stop:
        text = remove_stopwords(text)

    return text

def remove_stopwords(text):
    stopword_ru = stopwords.words('russian')
    stopword_ru.append('м')
    stopword_ru.append('это')
    stopword_ru.append('по')

    text = [w for w in text if w not in stopword_ru]

    return text
