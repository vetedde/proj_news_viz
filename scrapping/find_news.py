import csv
import io
import time

import feedparser

from .html_parser import get_html_links
from .store import Store, Downloader

FEEDS = 'data/parser/conf/feeds.csv'
SOURCES = 'data/parser/conf/sources.csv'
DOWNLOAD_ROOT = 'data/parser/cache'
SAVE_PATH = 'data/parser/lists/feed_urls.txt'

CACHE_TIME = 60 * 60

def csv2string(rows):
    si = io.StringIO()
    cw = csv.writer(si)
    for row in rows:
        cw.writerow(row)
    return si.getvalue().strip('\r\n').encode('utf-8')


class FeedLoader:
    def __init__(self, downloader):
        self.urls = set()
        self.downloader = downloader

    def load_feeds(self):
        with open(FEEDS, 'r') as f:
            items = [row for row in csv.reader(f)]

        for name, base_url, feed_url in items[1:]:
            body = self.downloader.load_url(feed_url, CACHE_TIME)
            print("Parsing feed", feed_url)
            feed = feedparser.parse(body)
            for f in feed.entries:
                url = f.get('link', '')
                if not url or url in self.urls:
                    continue
                self.urls.add(url)
                pub = time.strftime('%Y-%m-%dT%H:%M:%S', f.published_parsed)
                meta = csv2string({
                    'url': url,
                    'title': f.get('title', ''),
                    'summary': f.get('summary', ''),
                    'published': pub,
                    'feed_url': feed_url
                })
                self.downloader.save_extra(url, 'meta', meta)

    def load_main_pages(self):
        with open(SOURCES, 'r') as f:
            items = [row for row in csv.reader(f, delimiter='\t')]

        for row in items[1:]:
            if len(row) < 2:
                continue
            url = row[1]
            if '://' in url:
                urls = [url]
            else:
                urls = ['http://' + url, 'https://' + url]

            for url in urls:
                try:
                    base_url, body = self.downloader.load_url(url, CACHE_TIME)
                except Exception as e:
                    print(f"Error downloading page {url}: {e}")
                    continue
                print("Parsing page", url)
                for found_url in get_html_links(base_url, body):
                    self.urls.add(found_url)

    def process(self):
        self.load_feeds()
        self.load_main_pages()
        with open(SAVE_PATH, 'w') as f:
            f.write('\n'.join(sorted(self.urls)))


if __name__ == '__main__':
    fl = FeedLoader(Downloader(Store(DOWNLOAD_ROOT)))
    fl.process()
