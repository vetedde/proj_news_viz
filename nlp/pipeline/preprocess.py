import re
#from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem.wordnet import WordNetLemmatizer
# import pymorphy2  # pip install pymorphy2
# morph = pymorphy2.MorphAnalyzer()


def clean_text(text, russian_words_only: bool = False):
    """
    Cleaning text
    :param text:
    :param russian_words_only:
    :param remove_stop:
    :return:
    """

    text = text.lower()
    text = re.sub('ё', 'е', text.strip())
    if russian_words_only:
        text = re.sub("[^а-я]", ' ', text)
        text = text.strip('\n').strip('\r').strip('\t')

    else:
        text = text.strip('\n').strip('\r').strip('\t')

        text = re.sub("-\s\r\n\|-\s\r\n|\r\n", '', str(text))

        text = re.sub("[0-9]|[-—.,:;_%©«»?*!@#№$^•·&()]|[+=]|[[]|[]]|[/]|", '', text)
        text = re.sub(r"\r\n\t|\n|\\s|\r\t|\\n", ' ', text)
        text = re.sub(r'[\xad]|[\s+]', ' ', text.strip())
        text = re.sub(r'[\xad]|[\s+]', ' ', text.strip())

    # if remove_stop:
    #     text = remove_stopwords(text)
    text = [w for w in text.split() if w != '']
    return text

def remove_stopwords(text):
    """
    Removing stopwords.

    Add custom stopwords here.
    :param text:
    :return:
    """
    #stopword_ru = stopwords.words('russian')
    stopword_ru = []
    with open('stopwords.txt', 'r', encoding='utf-8') as f:
        for w in f.readlines():
            stopword_ru.append(w.strip())

    text = [w for w in text.split(' ') if w not in stopword_ru]

    return text
