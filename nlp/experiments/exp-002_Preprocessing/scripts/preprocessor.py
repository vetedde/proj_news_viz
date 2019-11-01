import os
import pickle

from nltk import sent_tokenize, wordpunct_tokenize


class Preprocessor(object):
    """
    Обертывает класс CSVCorpusReader и выполняет лексмезацию
    """
    def __init__(self, corpus, target=None, **Kwargs):
        """
        corpus - класс CSVCorpusReader
        target - директория для сохранения (prepare/rbc вводить)
        """
        self.corpus = corpus
        self.target = target

    def fileids(self, fileids=None, categories=None):
        fileids = self.corpus.resolve(fileids, categories)
        if fileids:
            return fileids
        return self.corpus.fileids()

    def abspath(self, fileid):
        # Найти путь к каталогу относительно корня исходного корпуса
        parent = os.path.relpath(
            os.path.dirname(self.corpus.abspath(fileid)), self.corpus.root
        )

        # Выделить части пути
        basename = os.path.basename(fileid)
        name, ext = os.path.splitext(basename)

        # Создать имя файля с расширением .pickle
        basename = name + '.pickle'
        print(basename)
        # Вернуть путь к файлу относительно корня целевого корпуса
        return os.path.normpath(os.path.join(self.target, parent, basename))

    def tokenize(self, fileid):
        for news in self.corpus.listcolumns(fileids=fileid):
            yield [
                wordpunct_tokenize(sent)
                for sent in sent_tokenize(news)
            ]

    def process(self, fileid):
        """
        Вызывается для файла, проверяет местоположение на
        диске, токенизирует методом tokenize для предварительной
        обработки и записывает трансформированный файл в виде
        сжатого архива в заданое место.
        """
        # Определить путь к файлу для записи результата
        target = self.abspath(fileid)
        parent = os.path.dirname(target)
        print('target', target)
        print('parent', parent)
        # Убедиться в существовании каталога
        if not os.path.isdir(parent):
            raise ValueError(
                "Пожалуйста укажите каталог для записи данных:"
            )

        # Создать структуру данных для записи в архив
        document = list(self.tokenize(fileid))

        # Записать данные в архив на диск
        with open(target, 'wb') as f:
            pickle.dump(document, f, pickle.HIGHEST_PROTOCOL)

        # Удалить документ из памяти
        del document

        # Вернуть путь к целевому каталогу
        return target

    def transform(self, fileids=None, categories=None):
        # Создать каталог, если его нет
        if not os.path.exists(self.target):
            os.makedirs(self.target)

        # Получить имена файлов для обработки
        return [
            self.process(fileid)
            for fileid in self.fileids(fileids, categories)
        ]
