data
--------

* **external** _(data from third party sources interim)_:
    - `news_lenta.csv` - _dataset lenta.ru from [here](https://www.kaggle.com/yutkin/corpus-of-russian-news-articles-from-lenta) (~700k rows; columns=['tags','text','title','topic','url']); download from github link_
  
* **interim** _(intermediate data that has been transformed)_:
    - `news_lenta-cleaned-lemmatize.csv.gz` - _cleaned & lemmatized 'title'+'text' dataset 'news_lenta.csv' (~675k rows; columns=['url','lemma_text'])_

* **processed** _(the final, canonical data sets for modeling)_:
    - `cleaned_name.pickle` - _to replace names to 1st form_

* **raw** _(the original, immutable data dump)_:
    - `...`

* **features** _(another files)_:
    - `stopwords_ru.txt` - _(624 samples)_