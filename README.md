# proj_news_viz


```bash
.
├── data
│   ├── parsed         #  2018-09-28.json.txt -- список скачанных статей в json
│   └── parser
│       ├── articles   # 0/a1/0a1b2c3d.html.gz -- кеш скачанных страниц
│       ├── conf       # feeds.csv, sources.csv , ...
│       └── lists      # download_urls.txt , processed_urls.txt , ...
├── README.md
└── scrapping          # скрипты для скраппинга
└── nlp                # скрипты и тетрадки по nlp
│   ├── topic_models   # тематическое моделирование
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

Здесь могло быть ваше имя.

## Make things work

 - [ ] входной файл для `scrapping/get_feed_url.py` (видимо `data/parser/lists/sources.txt`)
 - [ ] проверить, что `scrapping/get_feed_url.py` выдает файл нужного формата (`name;URL;feed_url`) `data/parser/lists/feeds.csv`
 - [ ] написать `rss-downloader`, из файла `data/parser/lists/feeds.csv` писать в файл ссылки на новости `/data/parser/lists/files_to_download.txt`
 - [ ] убедиться, что `scrapping/downloader/main.py` качает файлы (`hash.html.gz`) в `data/downloaded/date/`
 - [ ] (*) написать `crawling-parser`, который достает из скачанных файлов ссылки и дописывает их в файл для `downloader`а.
 - [ ] написать `article-parser`, который из файлов извлекает новости `{url, filename, title, text, collected_date}`
 - [ ] дедупликатор
 
 (*) ссылки для `downloader` докидывают и rss-downloader и crawling-parser, может быть race-condition с потерей ссылок от второго процесса, надо проверить.
