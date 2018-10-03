import os
import bs4
import requests
import csv
import feedparser
import traceback
from bs4 import BeautifulSoup

# Create a csv table with source name|URL|feed url

FEED_LINKS_ATTRIBUTES = (
    (('type', 'application/rss+xml'),),
    (('type', 'application/atom+xml'),),
    (('type', 'application/rss'),),
    (('type', 'application/atom'),),
    (('type', 'application/rdf+xml'),),
    (('type', 'application/rdf'),),
    (('type', 'text/rss+xml'),),
    (('type', 'text/atom+xml'),),
    (('type', 'text/rss'),),
    (('type', 'text/atom'),),
    (('type', 'text/rdf+xml'),),
    (('type', 'text/rdf'),),
    (('rel', 'alternate'), ('type', 'text/xml')),
    (('rel', 'alternate'), ('type', 'application/xml')),
)


def extract_feed_links(html, url, feed_links_attributes=FEED_LINKS_ATTRIBUTES):
    for attrs in feed_links_attributes:
        try:
            for link in html.findAll('link', dict(attrs)):
                    href = dict(link.attrs).get('href', '')
                    if '://' not in href:   # try URL absolute
                        href = url + str(link)
                    if href:
                        yield href
        except Exception as err:
            print('Oops. URL is invalid ', err)
            traceback.print_exc()


def get_rss_feed(sites):
    feeds_list = []
    for site in sites:
        if site is None:
            print('The URL should not be null!')
            continue
        else:
            if '://' not in site:  # try make right URL
                site = 'https://' + site
            source_code = requests.get(site)
            plain_text = source_code.text
            soup = BeautifulSoup(plain_text, 'lxml')
            head = soup.find('head')
            for link in extract_feed_links(head, site):
                if '://' not in link:  # make URL absolute
                    link = '://' + link
                feed = feedparser.parse(link)
                if not feed.get("bozo", 1):
                    feed = {"name": site, "URL": site, "feed_url": link}
                    feeds_list.append(feed)
    try:
        with open('feed.csv', 'w') as file:
            writer = csv.DictWriter(file,
                                    fieldnames=["name", "URL", "feed_url"],
                                    delimiter=';')
            writer.writeheader()
            for row in feeds_list:
                writer.writerow(row)
        print(feeds_list)
    except Exception as err:
        print('Oops. file is occured ', err)
        traceback.print_exc()
        pass


if __name__ == "__main__":
    url = ['https://ria.ru/', 'https://www.vesti.ru/news/',
           'meduza.io', 'https://russian.rt.com', 'https://www.axios.com/',
           'https://www.zerohedge.com/', 'http://lenta.ch/news']
    get_rss_feed(url)
