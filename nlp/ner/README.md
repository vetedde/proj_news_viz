data take from [this](print(cm.replace_keywords(text)))

about flashtext u can read [this](https://github.com/vi3k6i5/flashtext)


```
import cleanedNames as cm

# for example
text = '''абромавичус увидел гитлера и авраама линкольна врезав алешине'''

print(cm.extract_keywords(text))
>> ['авраам_линкольн']
print(cm.replace_keywords(text))
>> абромавичус увидел гитлера и авраам_линкольн врезав алешине
```
