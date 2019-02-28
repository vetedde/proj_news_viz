import csv
import gzip
import html
import io
import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import bleach
import bs4
import tqdm
from readability.readability import Document

from scrapping.uniscrape.links import Links
from scrapping.uniscrape.store import is_same_site, PageStore, FileStore, _load_page, RobotsParser, Page, get_sitename

csv.field_size_limit(sys.maxsize)

PAGE_CACHE_TIME = 86400 * 365 * 100  # 100 years
ROBOTS_CACHE_TIME = 86400 * 365  # 1 year

LISTS = Path('data/parser/lists')
SOURCES = 'data/parser/conf/sources.csv'


def get_sites():
    with open(SOURCES, 'r') as f:
        items = [row for row in csv.reader(f, delimiter='\t')]

    for row in items[1:]:
        if len(row) < 2:
            continue
        site_url = row[1]
        if '://' not in site_url:
            site_url = 'http://' + site_url
        yield get_sitename(site_url)


def get_html_links(robots: RobotsParser, page: Page):
    soup = bs4.BeautifulSoup(page.body, 'lxml')
    for element in soup.find_all('a', href=True):
        found_url = element.get('href', '')
        url = urljoin(page.url, found_url)
        if is_same_site(url, page.url):
            if robots.can_fetch(url):
                yield url


def html2text(text):
    text = bleach.clean(text, tags=['br', 'p', 'div', 'article', 'section', 'li', 'td', 'th', 'hr', 'dt'], strip=True)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'</?\w+[^>]*>', '\n', text)
    text = re.sub(r'\n\s+', '\n', text)
    text = re.sub(r'\s+\n', '\n', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def csv2string(rows):
    si = io.StringIO()
    cw = csv.writer(si)
    for row in rows:
        cw.writerow(row)
    return si.getvalue().strip('\r\n').encode('utf-8')


BAD_EXT = frozenset(['jpg', 'jpeg', 'png', 'gif', 'ico', 'mp3', 'wmv', 'wma', 'mp4', 'webp', 'flv', 'css', 'js'])
REBUILD_LINKS = True


def is_good_name(url):
    ext = url.rsplit('.')[-1]
    return ext not in BAD_EXT


def parse_file(sites: list, file_store: FileStore, robots: RobotsParser, src_path: Path):
    global all_links
    target_path = src_path.parent / src_path.name.replace('.html.gz', '.parsed.gz')
    if target_path.exists() and target_path.stat().st_size:
        if REBUILD_LINKS:
            with gzip.open(str(target_path), 'rt') as f:
                for row in csv.reader(f):
                    if row[0] == 'links':
                        for link in row[1].split('\n'):
                            all_links.add_link(link)

        return False
    fn = src_path.relative_to(file_store.root)
    # print("Rel path:", fn, "for", src_path)
    try:
        page = _load_page(file_store.load(str(fn)))
    except Exception:
        import traceback
        traceback.print_exc()
        return False

    site = get_sitename(page.url)
    mtime = str(src_path.stat().st_mtime)

    if site in sites and robots.can_fetch(page.url) and is_good_name(page.url) and page.body.strip():
        # print("Processing", target_path)
        try:
            doc = Document(page.body, url=page.url)

            # meta_path = src_path.parent / src_path.name.replace('.html.gz', '.meta.gz')

            links = get_html_links(robots, page)
            for link in links:
                all_links.add_link(link)
            info = {
                'status': 'OK',
                'url': page.url,
                'links': '\n'.join(links),
                'title': doc.short_title(),
                'text': html2text(doc.summary()),
                'downloaded': mtime,
            }
        except Exception:
            import traceback
            traceback.print_exc()
            info = {
                'status': 'ParseError',
                'url': page.url,
                'links': '',
                'title': '',
                'html': '',
                'downloaded': mtime,
            }

    else:
        info = {
            'url': page.url,
            'status': 'NotForRobots',
            'links': '',
            'title': '',
            'html': '',
            'downloaded': mtime,
        }
    # import pprint
    # pprint.pprint(info)

    ftmp = str(target_path) + '.tmp'
    with gzip.open(ftmp, 'wb') as f:
        f.write(csv2string(info.items()))
    os.rename(ftmp, target_path)

    return True


def main():
    global all_links
    sites = set(get_sites())
    root = Path('data/parser/articles/')
    file_store = FileStore(root)
    robots = RobotsParser(PageStore(file_store, ROBOTS_CACHE_TIME))
    all_links = Links(root / '../lists')

    ok, total = 0, 0
    search_root = root
    if len(sys.argv) > 1:
        search_root = root / sys.argv[1]
    print("Processsing files in", search_root)
    for fpath in tqdm.tqdm(list(search_root.rglob('*.html.gz'))):
        if parse_file(sites, file_store, robots, fpath):
            ok += 1
    print("Successful parse:", ok)


if __name__ == '__main__':
    main()
