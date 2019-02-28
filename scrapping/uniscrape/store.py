import datetime
import gzip
import hashlib
import os
import pathlib
import time
from collections import namedtuple
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from fake_useragent import UserAgent


def build_path(s: str, ext: str):
    fhash = str(hashlib.md5(s.encode()).hexdigest())
    return "{}/{}/{}.{}".format(fhash[:1], fhash[1:3], fhash[:20], ext)


class FileStore:
    def __init__(self, root):
        self.root = pathlib.Path(root)

    def load(self, fn: str):
        with gzip.open(self.root / fn, 'rb') as fin:
            return fin.read()

    def save(self, fn: str, body: bytes):
        fpath = self.root / fn
        ftmp = self.root / (fn + '.tmp')
        fpath.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(ftmp, 'wb', compresslevel=5) as fout:
            fout.write(body)
        os.rename(ftmp, fpath)

    def exists(self, fn, cache_time=None) -> bool:
        fpath = self.root / fn
        if not os.path.exists(fpath):
            return False
        if cache_time is None:
            return True
        expires = os.stat(fpath).st_mtime + cache_time
        return time.time() < expires


Page = namedtuple('Page', ('url', 'body'))


class URLStore:
    def __init__(self, store, cache_time):
        self.store = store
        self.cache_time = cache_time

    def load_url(self, url: str, file_ext: str = 'html'):
        fpath = build_path(url, file_ext + '.gz')
        return self.store.load(fpath)

    def save_url(self, url: str, body: bytes, file_ext: str = 'html'):
        assert isinstance(body, bytes)
        fpath = build_path(url, file_ext + '.gz')
        self.store.save(fpath, body)

    def exists(self, url: str, file_ext: str = 'html') -> bool:
        fpath = build_path(url, file_ext + '.gz')
        return self.store.exists(fpath, cache_time=self.cache_time)


def _load_page(content: bytes) -> Page:
    final_url, body = content.split(b'\n', 1)
    return Page(final_url.decode('utf-8'), body)


def _save_page(url: str, body: bytes):
    return url.encode('utf-8') + b'\n' + body


class PageStore(URLStore):
    def load_page(self, url: str) -> Page:
        return _load_page(self.load_url(url))

    def save_page(self, url: str, page: Page):
        assert isinstance(page, Page)
        if not is_same_site(url, page.url):
            self.save_url(url, _save_page(page.url, b'<!-- external URL -->'))
        else:
            raw = _save_page(page.url, page.body)
            self.save_url(url, raw)
            if page.url != url:
                self.save_url(page.url, raw)

    def save_empty_page(self, url: str):
        self.save_page(url, Page(url, b''))


def download_page(url: str, ua: str, timeout: int = 30):
    print("Downloading", url)
    headers = {'User-Agent': ua}
    try:
        with requests.get(url, headers=headers, timeout=timeout) as response:
            status_code = response.status_code
            body = response.text.encode('utf-8')
            return Page(response.url, body), status_code
    except Exception as e:
        print(f"While downloading, got exception: {type(e)} : {str(e)}")
        return Page(url, b''), 404  # not found


class Downloader:
    def __init__(self, store: PageStore):
        self.page_store = store
        self.ua = UserAgent()
        self.uar = self.ua.random
        self.robots = RobotsParser(store)

    def load_page(self, url: str):
        if self.exists(url):
            return self.page_store.load_page(url)
        else:
            page, status_code = download_page(url, self.uar)
            assert 200 <= status_code < 300, "Status code: {}".format(status_code)
            self.page_store.save_page(url, page)
            return page

    def exists(self, url: str):
        return self.page_store.exists(url)


def get_hostname(url):
    host = urlparse(url).hostname or ''
    return host


def get_sitename(url):
    host = get_hostname(url)
    if host.count('.') > 1:
        parts = host.split('.')
        if parts[-2] == 'co':  # e.g. www.site.co.uk
            host = '.'.join(parts[-3:])
        else:
            host = '.'.join(parts[-2:])
    return host


def is_same_site(url_a, url_b):
    return get_sitename(url_a) == get_sitename(url_b)


class RobotsParser:
    DISALLOW_ALL = b'User-agent: *\r\nDisallow: /'
    ALLOW_ALL = b'User-agent: *\r\nDisallow:'

    def __init__(self, store: URLStore):
        self.robots = {}
        self.store = store

    def get_robots_parser(self, url: str):
        rp = RobotFileParser()
        if self.store.exists(url, 'txt'):
            body = self.store.load_url(url, 'txt')
        else:
            page, status_code = download_page(url, 'Robot')
            body = page.body
            if status_code in [401, 403]:
                body = self.DISALLOW_ALL
            elif 400 <= status_code < 500:  # including status_code 404
                body = self.ALLOW_ALL
            self.store.save_url(url, body, 'txt')
        if body.strip() == self.ALLOW_ALL:
            rp.allow_all = True
        elif body.strip() == self.DISALLOW_ALL:
            rp.disallow_all = True
        else:
            rp.parse(body.decode('utf-8').splitlines())
        return rp

    def can_fetch(self, url: str):
        url_parts = urlparse(url)
        if not url_parts.scheme:
            return False
        domain = url_parts.scheme + '://' + url_parts.hostname
        rp = self.robots.get(domain, None)
        if rp is None:
            rp = self.robots[domain] = self.get_robots_parser(domain + '/robots.txt')
        return rp.can_fetch('*', url)


def build_dpid():
    dt = str(datetime.datetime.utcnow())
    return "{}-{}-{}".format(dt[:10].replace('-', '_'), dt[11:19].replace(':', '_'), os.getpid())


def main():
    rp = RobotsParser(PageStore(FileStore('/tmp'), 60))
    print(rp.can_fetch('https://www.mk.ru'))
    print(rp.can_fetch('www.mk.ru'))  # not http, not https


if __name__ == '__main__':
    main()
