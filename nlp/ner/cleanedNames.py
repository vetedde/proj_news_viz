# coding: utf-8
import pickle
from flashtext import KeywordProcessor # pip install flashtext

class KeyProc:

	with open('data/cleaned_name.pickle', 'rb') as handle:
		dict_cleaned_name = pickle.load(handle)
		
	kp = KeywordProcessor()
	kp = kp.add_keywords_from_dict(dict_cleaned_name)

	#def __init__(self, kp, dict_cleaned_name):
	#	self.kp = kp.add_keywords_from_dict(dict_cleaned_name)

	def extract_keywords(self, text):
		return self.kp.extract_keywords(text)

	def replace_keywords(self, text):
		return self.kp.replace_keywords(text)
