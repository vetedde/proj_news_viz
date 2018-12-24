in this this folder we extract names

* extracting_NER.ipynb - how create extraction
* cleaned_names.ipynb - how extracted complete names
* cleaned_names_rd.ipynb - r&d extraction (don't use in prod)
* cleanedNames.py - the main file which u can use for u using flashtext like this

```
import cleanedNames as cm

# for example
text = '''абромавичус увидел гитлера и авраама линкольна врезав алешине'''

print(cm.extract_keywords(text))
>> ['авраам_линкольн']
print(cm.replace_keywords(text))
>> абромавичус увидел гитлера и авраам_линкольн врезав алешине
```

p.s.

* data take from [this](print(cm.replace_keywords(text)))
* about flashtext u can read [this](https://github.com/vi3k6i5/flashtext)
