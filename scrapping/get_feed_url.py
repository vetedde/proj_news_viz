import os
import bs4
import requests
import csv
import feedparser
import traceback
from bs4 import BeautifulSoup
import urllib.parse

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

def extract_feed_links(html, base_url):
    soup = BeautifulSoup(html, 'lxml')
    head = soup.find('head')
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


def get_sites():
    with open(SOURCES, encoding='utf-8') as sources:
        reader = csv.reader(sources, delimiter='\t')
        data = [r for r in reader if len(r)>=2 and r[1:2] != ['Ссылка']]

    print(f"Found {len(data)} sites.")

    for row in data:
        name = row[0]
        site = row[1]
        if not '.' in site:
            print(f"Skipping bad site: {site}")
            continue
        if '://' in site:
            yield name, site
        else:
            yield name, 'http://' + site
            yield name, 'https://' + site

if __name__ == "__main__":
    feeds = []
    links = set()
    for name, site in get_sites():
        print(f"Fetching RSS for {name} at {site}")
        try:
            response = requests.get(site, timeout=30)
            url = response.url
            for link in extract_feed_links(response.text, url):
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
            #traceback.print_exc()

    with open(FEEDS, 'w', newline='') as f:
        writer = csv.writer(f)  # ["name", "URL", "feed_url"]
        writer.writerow(["name", "URL", "feed_url"])
        for row in feeds:
            writer.writerow(row)
    print(f"Found {len(feeds)} feeds.")
