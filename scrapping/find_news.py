import csv
import io
import time
from pathlib import Path

import feedparser

from .parse_news import get_html_links
from .store import Downloader, PageStore, is_same_site, FileStore, build_dpid, RobotsParser

FEEDS = 'data/parser/conf/feeds.csv'
SOURCES = 'data/parser/conf/sources.csv'
DOWNLOAD_ROOT = 'data/parser/articles'
LISTS = Path('data/parser/lists/')

CACHE_TIME = 60 * 10
TEST_MODE = False

def csv2string(rows):
    si = io.StringIO()
    cw = csv.writer(si)
    for row in rows:
        cw.writerow(row)
    return si.getvalue().strip('\r\n').encode('utf-8')


def load_feeds(downloader: Downloader):
    urls = set()
    with open(FEEDS, 'r') as f:
        items = [row for row in csv.reader(f)]

    for name, site_url, feed_url in items[1:]:
        if not TEST_MODE and downloader.exists(feed_url):
            continue
        try:
            body = downloader.load_page(feed_url)
            print("Parsing feed", feed_url)
        except Exception as e:
            print(f"Error downloading page {feed_url}: {e}")
            downloader.page_store.save_empty_page(feed_url)
            continue

        try:
            feed = feedparser.parse(body)
        except Exception as e:
            print(f"Error parsing page {feed_url}: {e}")
            continue

        for f in feed.entries:
            url = f.get('link', '')
            if not url or url in urls or not is_same_site(url, site_url):
                continue
            urls.add(url)
            pub = time.strftime('%Y-%m-%dT%H:%M:%S', f.published_parsed)
            meta = csv2string({
                'url': url,
                'title': f.get('title', ''),
                'summary': f.get('summary', ''),
                'published': pub,
                'feed_url': feed_url
            })
            downloader.page_store.save_url(url, meta, 'meta')
    return urls


def load_main_pages(downloader: Downloader):
    urls = set()
    with open(SOURCES, 'r') as f:
        items = [row for row in csv.reader(f, delimiter='\t')]

    for row in items[1:]:
        if len(row) < 2:
            continue
        site_url = row[1]
        if '://' in site_url:
            site_urls = [site_url]
        else:
            site_urls = ['http://' + site_url, 'https://' + site_url]

        for site_url in site_urls:
            if not TEST_MODE and downloader.exists(site_url):
                continue
            try:
                base_url, body = downloader.load_page(site_url)
            except Exception as e:
                downloader.page_store.save_empty_page(site_url)
                print(f"Error downloading {site_url}: {e}")
                import traceback
                traceback.print_exc()
                continue
            print("Parsing page", site_url)
            for found_url in get_html_links(base_url, body):
                urls.add(found_url)
    return urls


def main():
    file_store = FileStore(DOWNLOAD_ROOT)
    robots = RobotsParser(PageStore(file_store, 86400))  # one day
    downloader = Downloader(PageStore(file_store, CACHE_TIME))

    urls = load_feeds(downloader)

    for url in sorted(load_main_pages(downloader)):
        if not robots.can_fetch(url):
            print(f"Skipping {url}, forbidden by robots.txt")
        urls.add(url)

    if urls:
        dt, tm = build_dpid().split('-', 1)
        fn = f'{dt}/feeds-{tm}.txt'
        path = LISTS / fn
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(LISTS / fn, 'w') as f:
            f.write('\n'.join(sorted(urls)))
        print(f"Saved as {fn}")
    else:
        print("No urls.")


if __name__ == '__main__':
    main()
