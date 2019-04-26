in this this folder we extract names

by @marishadorosh:
* extracting_NER.ipynb - how create extraction

by @vtrokhymenko:
* cleaned_names.ipynb - how extracted complete names
* cleaned_names_rd.ipynb - r&d extraction (don't use in prod)
* cleanedNames.py - the main file which u can use for u using flashtext like this

```
from cleanedNames import KeyProc

# for example
text = '''когда дмитрий песков увидел владимира путина и авраама линкольна то подумал о иосифе сталине'''

cn = KeyProc()

print(cn.extractKeywords(text))
>> ['дмитрий_песков', 'владимир_путин', 'авраам_линкольн', 'иосиф_сталин']
print(cn.replaceKeywords(text))
>> когда дмитрий_песков увидел владимир_путин и авраам_линкольн то подумал о иосиф_сталин
```

p.s.

* data take from [this](https://github.com/ods-ai-ml4sg/proj_news_viz/blob/master/nlp/ner/print(cm.replace_keywords(text)))
* about flashtext u can read [this](https://github.com/vi3k6i5/flashtext)
