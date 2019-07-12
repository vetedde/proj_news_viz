# proj_news_viz  

## Что здесь происходит  
https://github.com/ods-ai-ml4sg/proj_news_viz/wiki/Start-Page

## Структура репозитория  

```bash
.
├── data
│   ├── parsed         #  2018-09-28.json.txt -- список скачанных статей в json
│   └── parser
│       ├── articles   # 0/a1/0a1b2c3d.html.gz -- кеш скачанных страниц
│       ├── conf       # feeds.csv, sources.csv , ...
│       └── lists      # download_urls.txt , processed_urls.txt , ...
├── README.md
├── scraping          # скрипты для скрапинга
├── nlp                # скрипты и тетрадки по nlp
│   ├── lemmatizers   # сравнение лемматизаторов
│   ├── preprocessing   # скрипты для предобработки сырых текстов
│   ├── ner   # распознавание именнованных сущностей
│   └── topic_models   # тематическое моделирование
│       └── experiments   # набор тетрадок с демонстрацией разных тематических моделей
│           ├── gensim, bigartm, etc...
```



## Requirements

Python 3.6+

## Порядок работы

1. Клонируем себе реп
2. Заводим ветку, кодим-проверяем-коммитим
3. Создаем пулл-реквест

## Соглашения

1. Не стесняйтесь писать комменты на русском языке.
2. Пишите содержательные сообщения к коммитам.
3. Используйте flake8 (`flake8 .`) для проверки кода на стиль.


## Contributions

- Andrey @Erlemar
- Vladimir @LanSaid
- Pavel @p-kachalov
- Andrey Malakhov @andreymalakhov
- Yuri Baburov @buriy
- Sviatoslav @iggisv9t  
Здесь могло быть ваше имя.

## Скрипты:

- scraping/downloader.py : скачивает страницы из списков, находящихся в data/parser/lists/*.txt
- scraping/find_feeds.py : заходит на сайты, находит все RSS на них и сохраняет в data/parser/conf/feeds.csv
- scraping/find_news.py : проходит по списку RSS и главных страниц и сохраняет все найденные ссылки
