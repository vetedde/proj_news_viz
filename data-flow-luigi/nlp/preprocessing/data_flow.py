# -*- coding: utf-8 -*-

import logging
import os
import sys
import re
import pymorphy2
import luigi
import luigi.retcodes

from nltk.corpus import stopwords
from razdel import tokenize

from luigi.contrib import hive
from luigi.task import flatten

logger = logging.getLogger(__name__)

cache = dict()
stopword_ru = stopwords.words('russian')
morph = pymorphy2.MorphAnalyzer()

from py_scripts.preprocessing import clean_text, lemmatization


class LoadStopWords(luigi.Task):
    date = luigi.DateParameter(description='Job launch date')
    stopwords_path = luigi.Parameter(description='Path to a stopwords file')
    
    def output(self):
        return luigi.LocalTarget(self.stopwords_path)

    def run(self):
        stopwords_russian = stopwords.words('russian')
        with open(self.stopwords_path, 'w') as f:
            for w in stopwords_russian:
                f.write(w+"\n")

class CleanLemmatize(luigi.Task):
    date = luigi.DateParameter(description='Job launch date')
    stopwords_path = luigi.Parameter(description='Path to a stopwords file')
    source_file = luigi.Parameter(description='Path to an input text file')
    target_file = luigi.Parameter(description='Path to an output text file (cleaned and lemmatized)')

    def output(self):
        return luigi.LocalTarget(self.target_file)

    def requires(self):
        return LoadStopWords(date=self.date, stopwords_path=self.stopwords_path)

    def run(self):
        with open(self.stopwords_path, 'r', encoding='utf-8') as f:
            for w in f.readlines():
                stopword_ru.append(w)

        text = open(self.source_file, 'r', encoding='utf-8').read()

        cleaned_text = clean_text(text)
        lemm_text = lemmatization(cleaned_text)
        with open(self.target_file, 'w') as f:
            f.write(" ".join(lemm_text))

if __name__ == "__main__":
    luigi.retcodes.run_with_retcodes(sys.argv[1:])

