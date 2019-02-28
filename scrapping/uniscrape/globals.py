import csv
import sys
from functools import lru_cache

from scrapping.uniscrape.conf import SOURCES, BAD_EXT, ROOT
from scrapping.uniscrape.sites import get_sitename, get_sites
from scrapping.uniscrape.store import RobotsParser, PageStore, FileStore

PAGE_CACHE_TIME = 86400 * 365 * 100  # 100 years
ROBOTS_CACHE_TIME = 86400 * 365  # 1 year

ALLOWED_SITES = None
ROBOTS = None
STORE = None


def is_allowed(url):
    global ALLOWED_SITES
    if ALLOWED_SITES is None:
        ALLOWED_SITES = set(get_sitename(u) for name, u in get_sites(SOURCES))
    return get_sitename(url) in ALLOWED_SITES


def is_good_url(url):
    if url.startswith('https://www.bbc.com/') and not url.startswith('https://www.bbc.com/russian'):
        return False
    ext = url.rsplit('.')[-1]
    return ext not in BAD_EXT


def get_store():
    global STORE
    if STORE is None:
        STORE = PageStore(FileStore(ROOT), PAGE_CACHE_TIME)
    return STORE


def can_fetch(url):
    global ROBOTS
    if ROBOTS is None:
        ROBOTS = RobotsParser(PageStore(FileStore(ROOT), ROBOTS_CACHE_TIME))

    if url.startswith('https://www.kommersant.ru/doc/'):
        return True
    return ROBOTS.can_fetch(url)


@lru_cache(maxsize=10000000)
def is_all_cool(url):
    if not url or not url.strip(): return False
    url = url.strip()
    if not is_allowed(url):
        return False
    if not is_good_url(url):
        return False
    if not can_fetch(url):
        return False
