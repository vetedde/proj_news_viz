luigi-задача для обработки текста.
1. Читает файл с текстом, который нужно обработать.
2. Делает лемматизацию 
3. Сохраняет также в обычном текстовом формате на диск

Пример запуска:
```
export DATE=$(date +"%Y-%m-%d" -d "1 day ago")
export LUIGI_CONFIG_PATH=./config/test.cfg
python -m data_flow CleanLemmatize --date=$DATE
```
