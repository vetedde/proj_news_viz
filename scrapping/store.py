import gzip
import hashlib
import os
import pathlib
import time

import requests
from fake_useragent import UserAgent


class Store:
    def __init__(self, root):
        self.root = pathlib.Path(root)

    def load(self, fn: str):
        with gzip.open(self.root / fn, 'rb') as fin:
            return fin.read()

    def save(self, fn, body: bytes):
        fpath = self.root / fn
        fpath.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(fpath, 'wb', compresslevel=5) as fout:
            fout.write(body)

    def exists(self, fn, cache_time=None):
        fpath = self.root / fn
        if not os.path.exists(fpath):
            return False
        if cache_time is None:
            return True
        expires = os.stat(fpath).st_mtime + cache_time
        return time.time() < expires


def build_path(s: str, ext: str):
    fhash = str(hashlib.md5(s.encode()).hexdigest())
    return "{}/{}/{}.{}".format(fhash[:1], fhash[1:3], fhash[:20], ext)


class Downloader:
    def __init__(self, store):
        self.store = store
        self.ua = UserAgent()

    def download_url(self, url: str):
        print("Downloading", url)
        headers = {'User-Agent': self.ua.random}
        with requests.get(url, headers=headers, timeout=30) as response:
            assert 200 <= response.status_code < 299
            return response.url, response.text

    def load_url(self, url: str, cache_time: int):
        fpath = build_path(url, 'html.gz')
        if not self.store.exists(fpath, cache_time):
            base_url, body = self.download_url(url)
            self.store.save(fpath, (base_url + '\n' + body).encode('utf-8'))
            return base_url, body
        url, body = self.store.load(fpath).decode('utf-8').split('\n', 1)
        return url, body

    def save_extra(self, url: str, ext: str, data: bytes):
        fn = build_path(url, ext + '.gz')
        self.store.save(fn, data)
