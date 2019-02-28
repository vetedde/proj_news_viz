import csv
import datetime
import gzip
import sys
from collections import Counter
from pathlib import Path

from scrapping.uniscrape.archive import process_archive
from scrapping.uniscrape.conf import ROOT
from scrapping.uniscrape.sites import get_sitename


def parse_file(src_path: Path):
    target_path = src_path.parent / src_path.name.replace('.html.gz', '.parsed.gz')
    if target_path.exists() and target_path.stat().st_size:
        with gzip.open(str(target_path), 'rt') as f:
            info = {k: v for k, v in csv.reader(f)}
            save_entry(info)
    return {}


TARGET_ROOT = Path('data/parser/dataset/')
TARGET_FILES = {}
TARGET_COUNTS = Counter()


def save_entry(info):
    global TARGET_FILES

    site = get_sitename(info['url'])
    target_file = TARGET_ROOT / site
    if site not in TARGET_FILES:
        f = open(target_file, 'w')
        f = csv.writer(f)
        f.writerow(('downloaded', 'url', 'status', 'title', 'text'))
        TARGET_FILES[site] = f
    else:
        f = TARGET_FILES[site]
    dt = datetime.datetime.fromtimestamp(int(float(info['downloaded'])))
    f.writerow((dt,
                info['url'],
                info['status'],
                info['title'],
                info.get('text', info.get('html', ''))))

    TARGET_COUNTS[site] += 1


def main():
    ok = 0
    search_root = ROOT
    if len(sys.argv) > 1:
        search_root = ROOT / sys.argv[1]
    for fpath in process_archive(search_root):
        if parse_file(fpath):
            ok += 1
    print("Successful parse:", ok)
    print(TARGET_COUNTS.most_common())


if __name__ == '__main__':
    main()
