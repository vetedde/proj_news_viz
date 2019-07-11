Пример запуска:
```
export DATE=$(date +"%Y-%m-%d" -d "1 day ago")
export LUIGI_CONFIG_PATH=./config/test.cfg
python -m data_flow CleanLemmatize --date=$DATE
```

