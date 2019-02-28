import csv
import gzip
import os
import sys
from pathlib import Path

import tqdm

from scrapping.uniscrape.archive import process_archive
from scrapping.uniscrape.conf import ROOT
from scrapping.uniscrape.globals import is_allowed, is_good_url, can_fetch


def parse_file(src_path: Path):
    target_path = src_path.parent / src_path.name.replace('.html.gz', '.parsed.gz')
    if target_path.exists() and target_path.stat().st_size:
        with gzip.open(str(target_path), 'rt') as f:
            for row in csv.reader(f):
                if row[0] == 'url':
                    url = row[1].strip()
                    if not url:
                        return False
                    remove = False

                    if not is_allowed(url):
                        remove = True
                    elif not is_good_url(url):
                        remove = True
                    elif not can_fetch(url):
                        remove = True

                    if remove:
                        # print("Removing URL:", url, 'paths:', target_path, src_path)
                        os.unlink(target_path)
                        os.unlink(src_path)
                        return True
    return False


def main():
    ok = 0
    search_root = ROOT
    if len(sys.argv) > 1:
        search_root = ROOT / sys.argv[1]
    for fpath in process_archive(search_root):
        if parse_file(fpath):
            ok += 1
    print("Successful parse:", ok)


if __name__ == '__main__':
    main()
