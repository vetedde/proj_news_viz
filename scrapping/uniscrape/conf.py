from pathlib import Path

ROOT = Path('data/parser/articles/')
LOGS = Path('data/parser/logs/')
LISTS = Path('data/parser/lists')
SOURCES = 'data/parser/conf/sources.csv'
BAD_EXT = frozenset(['jpg', 'jpeg', 'png', 'gif', 'ico', 'mp3', 'wmv', 'wma', 'mp4', 'webp', 'flv', 'css', 'js'])
