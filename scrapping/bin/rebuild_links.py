import csv
import gzip
import sys
from pathlib import Path

from scrapping.uniscrape.archive import process_archive
from scrapping.uniscrape.conf import ROOT, LISTS
from scrapping.uniscrape.globals import is_all_cool
from scrapping.uniscrape.links import Links

all_links = Links(LISTS)


def parse_file(src_path: Path):
    target_path = src_path.parent / src_path.name.replace('.html.gz', '.parsed.gz')
    if target_path.exists() and target_path.stat().st_size:
        with gzip.open(str(target_path), 'rt') as f:
            for row in csv.reader(f):
                if row[0] == 'links':
                    for link in row[1].split('\n'):
                        if is_all_cool(link):
                            all_links.add_link(link)

        return False
    return False


def main():
    root = Path(ROOT)

    ok = 0
    search_root = root
    if len(sys.argv) > 1:
        search_root = root / sys.argv[1]
    for fpath in process_archive(search_root):
        if parse_file(fpath):
            ok += 1
    print("Successful parse:", ok)


if __name__ == '__main__':
    main()
