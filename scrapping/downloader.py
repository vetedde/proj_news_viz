import argparse
import asyncio
import csv
import datetime
import gzip
import hashlib
import os
import pathlib
import random
import time
import traceback
import typing
from collections import defaultdict
from urllib.parse import urlparse, urldefrag

from aiohttp import web, ClientSession

ALL_URLS = set()


class Entry:
    source: str
    url: str
    attempts: int

    def __init__(self, url, source=None):
        assert isinstance(url, str)
        url = urldefrag(url).url
        self.host = urlparse(url).netloc.rstrip(':80').rstrip(':443')
        self.source = source or self.host
        if self.host.startswith('www.'):
            self.host = self.host[len('www.'):]
        self.url = url
        self.attempts = 0

    def __str__(self):
        return f"<Entry: {self.url}>"

def build_path(s: str):
    print(s)
    fhash = str(hashlib.md5(s.encode()).hexdigest())
    return "{}/{}/{}.html.gz".format(fhash[:1], fhash[1:3], fhash)


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


class Downloader:
    HOST_SLEEP_TIME = 1

    def __init__(self, download_root, log_root):
        self.log_root = pathlib.Path(log_root)
        self.download_root = pathlib.Path(download_root)
        self.log_file = None
        self.log_started = time.time()
        self.queues = defaultdict(list)

    def log(self, entry: Entry, fpath: str, success: bool):
        if self.log_file is None or time.time() > self.log_started + 900:
            log_fpath = self.log_root / build_dpid() + '.csv'
            log_fpath.parent.mkdir(parents=True, exist_ok=True)
            self.log_file = csv.writer(open(log_fpath, 'w', newline=''))
                            #fieldnames=["source", "URL", "status", "attempts", "fpath"])
        status = 'OK' if success else 'Error'
        self.log_file.writerow((entry.source, entry.url, status, entry.attempts, fpath))

    async def fetch_url(self, entry: Entry, session: ClientSession):
        print("Fetch", entry)
        try:
            async with session.get(entry.url, timeout=30) as response:
                body = await response.read()
            fpath = self.download_root / build_path(entry.url)
            fpath.parent.mkdir(parents=True, exist_ok=True)
            with gzip.open(fpath, 'wb', compresslevel=5) as fout:
                fout.write(body)
                self.log(entry, fpath, True)
        except Exception:
            traceback.print_exc()
            entry.attempts += 1

            if entry.attempts >= 3:
                # didn't make it
                self.log(entry, fpath, False)
            else:
                # try again
                await self.enqueue(entry)

    async def fetch_host(self, queue: typing.List[Entry]):
        async with ClientSession() as session:
            while queue:
                url = queue.pop()
                await self.fetch_url(url, session)
                await asyncio.sleep(self.HOST_SLEEP_TIME)

    async def enqueue(self, entry: Entry):
        print("Enqueue", entry)
        queue = self.queues[entry.host]
        queue.append(entry)

        if len(queue) == 1:
            # queue for this host is empty -- start new fetch_host
            await self.fetch_host(queue)

    def exists(self, entry):
        return (self.download_root / build_path(entry.url)).exists()


async def watch_file(path, downloader, interval=60):
    while True:
        for line in load_from_file(path):
            line = line.strip()
            if not line:
                continue
            entry = Entry(line.strip())
            print(f"Checking {entry}")
            if entry.url in ALL_URLS:
                continue
            if downloader.exists(entry):
                continue
            ALL_URLS.add(entry.url)
            await downloader.enqueue(entry)
        await asyncio.sleep(interval)


def run_test_server():
    async def handle(request):
        await asyncio.sleep(random.randint(0, 3))
        return web.Response(text="Hello, World!")

    app = web.Application()
    app.router.add_route('GET', '/{name}', handle)
    web.run_app(app)


def main(args):
    os.makedirs(args.download_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)
    downloader = Downloader(args.download_dir, args.log_dir)

    loop = asyncio.get_event_loop()

    if args.test_server:
        run_test_server()

    loop.run_until_complete(watch_file(args.input_file, downloader=downloader, interval=args.interval))


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str,
                        default='data/parser/lists/files_to_download.txt')
    parser.add_argument('--download_dir', type=str,
                        default='data/parser/downloaded/')
    parser.add_argument('--log_dir', type=str,
                        default='data/parser/logs/')
    parser.add_argument('--interval', type=int, default=60)
    parser.add_argument('--test-server', type=bool,
                        default=False)

    return parser.parse_args()


if __name__ == "__main__":
    _args = _parse_args()
    main(_args)
