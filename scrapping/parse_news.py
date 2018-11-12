import csv
import datetime
import gzip
import os
from pathlib import Path
from urllib.parse import urljoin

import bs4
import tqdm

from scrapping.store import is_same_site

ARTICLES = Path('data/parser/articles/')
LOGS = Path('data/parser/logs/')
LISTS = Path('data/parser/lists')


def get_html_links(base_url, body):
    soup = bs4.BeautifulSoup(body, 'lxml')
    for element in soup.find_all('a', href=True):
        url = element.get('href', '')
        url = urljoin(base_url, url)
        if is_same_site(url, base_url):
            yield urljoin(base_url, url)


def find_files_to_parse(logs):
    files = set()
    for log_path in logs:
        # print("Processing", log_path)
        try:
            lines = list(csv.reader(open(log_path, 'r')))
        except Exception as e:
            print(f"File: {log_path} Exception: {e}")
            import traceback;
            traceback.print_exc()
            yield log_path, None
            continue
        for parts in lines:
            if len(parts) != 5:
                # print("Bad info:", parts)
                continue
            site, url, status, attempts, fpath = parts
            if fpath in files: continue
            files.add(fpath)
            yield None, fpath
        yield log_path, None


def build_dpid():
    dt = str(datetime.datetime.utcnow())
    return "{}/{}-{}".format(dt[:10], dt[11:19].replace(':', '_'), os.getpid())


def find_urls(files):
    unique_urls = set()
    new_urls = []
    urls_counter = tqdm.tqdm()
    processed = []

    for log_path, fpath in tqdm.tqdm(files):
        if log_path:
            processed.append(log_path)
            continue

        if not (ARTICLES / fpath).exists():
            continue

        try:
            with gzip.open(ARTICLES / fpath, 'rb') as file:
                base_url, html = file.read().decode('utf-8').split('\n', 1)
        except Exception:
            continue

        for url in get_html_links(base_url, html):
            if url not in unique_urls:
                unique_urls.add(url)
                new_urls.append(url)
                urls_counter.update(1)

        if len(new_urls) > 10000:
            yield processed, new_urls
            processed = []
            new_urls = []

    if new_urls:
        yield processed, new_urls
    urls_counter.close()


def main():
    files = list(find_files_to_parse(LOGS.glob('201?-??-??/*.csv')))

    for processed, new_urls in find_urls(files):
        dpid = build_dpid()
        with open(LISTS / f'parsed-{dpid}.txt', 'w+') as file:
            for url in new_urls:
                file.write(url + '\n')

        for fpath in processed:
            os.rename(fpath, str(fpath) + '.crawled')


if __name__ == '__main__':
    main()
