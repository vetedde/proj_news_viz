import csv
import traceback
import urllib.parse

import feedparser
from bs4 import BeautifulSoup

from scrapping.uniscrape.store import Downloader

# Create a csv table with source name|URL|feed url
SOURCES = 'data/parser/conf/sources.csv'
FEEDS = 'data/parser/conf/feeds.csv'

FEED_LINKS_ATTRIBUTES = (
    {'type': 'application/rss+xml'},
    {'type': 'application/atom+xml'},
    {'type': 'application/rss'},
    {'type': 'application/atom'},
    {'type': 'application/rdf+xml'},
    {'type': 'application/rdf'},
    {'type': 'text/rss+xml'},
    {'type': 'text/atom+xml'},
    {'type': 'text/rss'},
    {'type': 'text/atom'},
    {'type': 'text/rdf+xml'},
    {'type': 'text/rdf'},
    {'rel': 'alternate', 'type': 'text/xml'},
    {'rel': 'alternate', 'type': 'application/xml'},
)


def extract_feed_links(base_url, html):
    soup = BeautifulSoup(html, 'lxml')
    for attrs in FEED_LINKS_ATTRIBUTES:
        try:
            for link in soup.findAll('link', attrs):
                href = link.attrs.get('href', '')
                if href:
                    yield urllib.parse.urljoin(base_url, href)
            for link in soup.findAll('link') + soup.findAll('a'):
                href = link.attrs.get('href', '')
                if 'rss' in href or 'atom' in href:
                    yield urllib.parse.urljoin(base_url, href)
        except Exception:
            traceback.print_exc()


def main():
    feeds = []
    links = set()
    d = Downloader(None)
    for name, site in get_sites(SOURCES):
        print(f"Fetching RSS for {name} at {site}")
        try:
            base_url, body = d.download_url(site)
            for link in extract_feed_links(base_url, body):
                if link in links:
                    continue
                links.add(link)
                print(f"Trying {link}...")
                feed = feedparser.parse(link)
                if not feed.get("bozo", 1):
                    print("Success!")
                    feeds.append((name, site, link))
        except Exception as e:
            print(f"Error: {e}")
            # traceback.print_exc()

    with open(FEEDS, 'w', newline='') as f:
        writer = csv.writer(f)  # ["name", "URL", "feed_url"]
        writer.writerow(["name", "URL", "feed_url"])
        for row in feeds:
            writer.writerow(row)
    print(f"Found {len(feeds)} feeds.")


if __name__ == "__main__":
    main()
