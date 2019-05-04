Extracting names

by @marishadorosh:
* extracting_NER.ipynb - how to create extraction

by @vtrokhymenko:
* cleaned_names.ipynb - how names was extracted
* cleaned_names_rd.ipynb - r&d extraction (don't use in prod)
* cleanedNames.py - the main file which u can use for using flashtext like this

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

* data from [here](https://newsviz.s3.nl-ams.scw.cloud/misc/cleaned_names.csv)
* about flashtext u can read [here](https://github.com/vi3k6i5/flashtext)
