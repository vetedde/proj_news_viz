# Async Downloader

Запускать в корне проекта
```bash
python scrapping/downloader/main.py
```

Смотрит в файл `data/parser/lists/files_to_download.txt`, пишет в `data/parser/downloaded`.
Лог пишется `/tmp/{:%Y-%m-%d}.log`

Для тестирования рядом есть асинхронный сервер, запустится на 8080 порту:
```bash
python scrapping/downloader/server.py
```