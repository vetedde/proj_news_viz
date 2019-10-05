# coding: utf-8
import pickle
from flashtext import KeywordProcessor # pip install flashtext

class KeyProc:
    
    with open('../data/cleaned_name.pickle', 'rb') as handle:
        dict_cleaned_name = pickle.load(handle)

    def __init__(self, dict = dict_cleaned_name):
        #self.text = text
        self.kp = KeywordProcessor()
        self.kp.add_keywords_from_dict(dict)

    def extractKeywords(self, text):
        return self.kp.extract_keywords(text)

    def replaceKeywords(self, text):
        return self.kp.replace_keywords(text)
