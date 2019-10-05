# coding: utf-8
import pickle
from flashtext import KeywordProcessor # pip install flashtext

class KeyProc:
    
    def __init__(self,  main_path=None):
        """
        Parameters
        ----------
            main_path : string
                path to project
        """
    
        with open(f'{main_path}/data/processed/cleaned_name.pickle', 'rb') as handle:
            self.dict_cleaned_name = pickle.load(handle)

        self.kp = KeywordProcessor()
        self.kp.add_keywords_from_dict(self.dict_cleaned_name)

    def extractKeywords(self, text):
        return self.kp.extract_keywords(text)

    def replaceKeywords(self, text):
        return self.kp.replace_keywords(text)