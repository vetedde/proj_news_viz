replace persons
----

by @vtrokhymenko:
* vt-replace_persons.ipynb - how names was extracted
* vt-replace_persons_test.ipynb - r&d extraction (don't use in prod)
* replace_persons.py - the main file which u can use for using flashtext like this

```
from replace_persons import KeyProc

# for example
text = '''когда дмитрий песков увидел владимира путина и авраама линкольна то подумал о иосифе сталине'''

rp = KeyProc()

print(rp.extractKeywords(text))
>> ['дмитрий_песков', 'владимир_путин', 'авраам_линкольн', 'иосиф_сталин']
print(rp.replaceKeywords(text))
>> когда дмитрий_песков увидел владимир_путин и авраам_линкольн то подумал о иосиф_сталин
```

p.s.
* data from [here](https://newsviz.s3.nl-ams.scw.cloud/misc/cleaned_names.csv)
* about flashtext u can read [here](https://github.com/vi3k6i5/flashtext)
