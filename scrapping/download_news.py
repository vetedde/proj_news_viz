import argparse
import asyncio
import csv
import datetime
import os
import pathlib
import random
import time
import traceback
from collections import defaultdict
from urllib.parse import urlparse, urldefrag

from aiohttp import web, ClientSession
from fake_useragent import UserAgent

from scrapping.store import Store, build_path

ALL_URLS = set()


class Entry:
    source: str
    url: str
    attempts: int

    def __init__(self, url, source=None):
        assert isinstance(url, str)
        url = urldefrag(url).url
        self.host = urlparse(url).hostname.rstrip(':80').rstrip(':443')
        self.source = source or self.host
        if self.host.startswith('www.'):
            self.host = self.host[len('www.'):]
        self.url = url
        self.attempts = 0

    def __str__(self):
        return f"<Entry: {self.url}, errors: {self.attempts}>"


def build_dpid():
    dt = str(datetime.datetime.utcnow())
    return "{}/{}-{}".format(dt[:10], dt[11:19].replace(':', '_'), os.getpid())


def load_from_file(fpath: str):
    with open(fpath, 'r') as fin:
        urls = [line.strip() for line in fin.readlines()]
    for url in urls:
        if len(url) == 0:  # just avoid empty lines in input file
            continue
        yield url


class Logger:
    ROTATION_TIME = 900

    def __init__(self, log_root):
        self.log_root = pathlib.Path(log_root)
        self.log_root.mkdir(parents=True, exist_ok=True)
        self.log_file = None
        self.log_started = time.time()

    def rotate_log(self):
        log_fpath = self.log_root / build_dpid()
        log_fpath.parent.mkdir(parents=True, exist_ok=True)
        self.log_file = csv.writer(open(str(log_fpath) + '.csv', 'w', newline=''))

    def log(self, entry: Entry, fpath: str, success: bool):
        if self.log_file is None or time.time() > self.log_started + self.ROTATION_TIME:
            self.rotate_log()
        status = 'OK' if success else 'Error'
        # fieldnames=["source", "URL", "status", "attempts", "fpath"])
        self.log_file.writerow((entry.source, entry.url, status, entry.attempts, fpath))


class AsyncDownloader:
    HOST_SLEEP_TIME = 1
    PAGE_CACHE_TIME = 86400 * 90  # 90 days

    def __init__(self, store, logger):
        self.logger = logger
        self.store = store
        self.ua = UserAgent()
        self.queues = defaultdict(lambda: (asyncio.Lock(), list()))

    async def fetch_url(self, entry: Entry, session: ClientSession):
        fpath = build_path(entry.url, 'html.gz')
        if self.store.exists(fpath, self.PAGE_CACHE_TIME):
            print("Already downloaded", entry)
            return True
        print("Downloading", entry)
        try:
            headers = {'User-Agent': self.ua.random}
            async with session.get(entry.url, headers=headers, timeout=30) as response:
                body = await response.read()
                base_url = str(response.url)
                #print(f"For {entry.url} base_url={base_url} type(body)={type(body)}")
                payload = base_url.encode('utf-8') + b'\n' + body

            self.store.save(fpath, payload)
            self.logger.log(entry, fpath, True)

            if base_url != entry.url:
                # XXX: If the crawler was redirected to a new URL, save it under both old URL and new URL
                fpath_base = build_path(base_url, 'html.gz')
                if not self.store.exists(fpath_base, self.PAGE_CACHE_TIME):
                    self.store.save(fpath_base, payload)

            return True
        except Exception:
            traceback.print_exc()
            self.logger.log(entry, fpath, False)
            return False

    async def fetch_host(self, host):
        lock, queue = self.queues[host]
        async with lock:
            async with ClientSession() as session:
                while queue:
                    url = queue.pop()
                    success = await self.fetch_url(url, session)
                    if not success and url.attempts < 3:
                        url.attempts += 1
                        queue.append(url)
                    await asyncio.sleep(self.HOST_SLEEP_TIME)

    def enqueue(self, entry: Entry):
        if self.store.exists(build_path(entry.url, 'html.gz')):
            return False

        print("Enqueue", entry)
        host = entry.host
        _, queue = self.queues[host]
        queue.append(entry)

        if len(queue) == 1:
            # queue for this host was empty -- start new fetch_host
            loop = asyncio.get_event_loop()
            loop.create_task(self.fetch_host(host))
        return True

    def exists(self, entry):
        return self.store.exists(build_path(entry.url, 'html.gz'))


async def watch_file(path, downloader, interval):
    while True:
        for fn in os.listdir(path):
            new_entries = 0
            for line in load_from_file(os.path.join(path, fn)):
                line = line.strip()
                if not line:
                    continue
                entry = Entry(line.strip())
                if entry.url in ALL_URLS:
                    continue
                new_entries += 1
                ALL_URLS.add(entry.url)
                downloader.enqueue(entry)
            print(f"Added {new_entries} entries from {fn}.")
        await asyncio.sleep(interval)


def run_test_server():
    async def handle(request):
        await asyncio.sleep(random.randint(0, 3))
        return web.Response(text="Hello, World!")

    app = web.Application()
    app.router.add_route('GET', '/{name}', handle)
    web.run_app(app)


def main(args):
    store = Store(args.download_dir)
    logger = Logger(args.log_dir)
    downloader = AsyncDownloader(store, logger)

    loop = asyncio.get_event_loop()

    if args.test_server:
        run_test_server()

    watchdog = watch_file(args.input_dir,
                          downloader=downloader,
                          interval=args.interval)
    try:
        loop.run_until_complete(watchdog)
    except KeyboardInterrupt:
        # Wait 250 ms for the underlying SSL connections to close
        loop.run_until_complete(asyncio.sleep(0.250))
        print("Exiting after Ctrl-C")


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, default='data/parser/lists/')
    parser.add_argument('--download_dir', type=str, default='data/parser/articles/')
    parser.add_argument('--log_dir', type=str, default='data/parser/logs/')
    parser.add_argument('--interval', type=int, default=30)
    parser.add_argument('--test-server', type=bool, default=False)

    return parser.parse_args()


if __name__ == "__main__":
    _args = _parse_args()
    main(_args)
