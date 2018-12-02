import re
from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem.wordnet import WordNetLemmatizer
# import pymorphy2  # pip install pymorphy2
# morph = pymorphy2.MorphAnalyzer()


def clean_text(text, russian_words_only: bool = False, remove_stop: bool = True):
    """
    Cleaning text
    :param text:
    :param russian_words_only:
    :param remove_stop:
    :return:
    """

    text = text.lower()
    if russian_words_only:
        text = re.sub("[^а-я]", ' ', text)
        text = text.strip('\n').strip('\r').strip('\t')

    else:
        text = re.sub("-\s\r\n\|-\s\r\n|\r\n", '', str(text))

        text = re.sub("[0-9]|[-.,:;_%©?*!@#№$^•·&()]|[+=]|[[]|[]]|[/]|", ' ', text)
        text = re.sub(r"\r\n\t|\n|\\s|\r\t|\\n", ' ', text)
        text = re.sub(r'[\xad]|[\s+]', ' ', text)
        text = re.sub('ё', 'е', text.strip())

    if remove_stop:
        text = remove_stopwords(text)
    text = [w for w in text if w != '']
    return text

def remove_stopwords(text):
    """
    Removing stopwords.

    Add custom stopwords here.
    :param text:
    :return:
    """
    stopword_ru = stopwords.words('russian')
    with open('stopwords.txt', 'r', encoding='utf-8') as f:
        for w in f.readlines():
            stopword_ru.append(w)

    text = [w for w in text.split(' ') if w not in stopword_ru]

    return text
