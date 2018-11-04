import csv
import datetime
import gzip
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import bs4
import tqdm

ARTICLES = Path('data/parser/articles/')
LOGS = Path('data/parser/logs/')
LISTS = Path('data/parser/lists')


def get_html_links(base_url, body):
    base_parsed = urlsplit(base_url, scheme='http')
    # print('get_html_links:', base_url, len(body))
    base_domain = base_parsed.netloc
    if base_domain.count('.') > 1:
        parts = base_domain.split('.')
        if parts[-2] == 'co':  # e.g. www.site.co.uk
            base_domain = '.'.join(parts[-3:])
        else:
            base_domain = '.'.join(parts[-2:])
    soup = bs4.BeautifulSoup(body, 'lxml')

    for element in soup.find_all('a', href=True):
        url = element.get('href', '')

        parsed_url = urlsplit(url, scheme=base_parsed.scheme)
        if parsed_url.scheme not in ['', 'http', 'https']:
            continue
        if parsed_url.netloc:  # this is an absolute link
            domain = '.' + parsed_url.netloc
            if not domain.endswith('.' + base_domain):
                continue

        yield urljoin(base_url, url)


def process_html_file(html_path: str, save_path: str):
    """
    Html parser for self reference links
    html_parser parses html document for links belonging to
    the same domain and stores it to txt file with one URL per
    line.
    Arguments:
        html_path (str): Path to html file.
        base_url (str): Domain name to search for.
        save_path (str): Path for output file
    """


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
    last_unique_urls = set()
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
            last_unique_urls = set(unique_urls)
            processed = []
            new_urls = []

    if new_urls:
        yield processed, new_urls
    urls_counter.close()


if __name__ == '__main__':
    files = list(find_files_to_parse(LOGS.glob('201?-??-??/*.csv')))

    for processed, new_urls in find_urls(files):
        dpid = build_dpid().replace('/', '-')
        with open(LISTS / f'parsed-{dpid}.txt', 'w+') as file:
            for url in new_urls:
                file.write(url + '\n')

        for fpath in processed:
            os.rename(fpath, str(fpath) + '.crawled')
