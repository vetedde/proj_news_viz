# proj_news_viz  

## Что здесь происходит
### Ответы на все вопросы первым делом искать тут:  
https://github.com/ods-ai-ml4sg/proj_news_viz/wiki

## Структура репозитория  

```bash
.
├── README.md
├── visualization      # всячина связанная с визуализацией
├── scraping           # скрипты для скрапинга
├── nlp                # всё, что связано с nlp в проекте
│   ├──                # см. readme внутри
├── data-flow-luigi/nlp # зачатки продуктового пайплайна
├── data
│   ├── parsed         #  2018-09-28.json.txt -- список скачанных статей в json
│   └── parser
│       ├── articles   # 0/a1/0a1b2c3d.html.gz -- кеш скачанных страниц
│       ├── conf       # feeds.csv, sources.csv , ...
│       └── lists      # download_urls.txt , processed_urls.txt , ...
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
