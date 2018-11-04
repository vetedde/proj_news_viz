import argparse
import asyncio
import csv
import datetime
import os
import pathlib
import random
import time
from urllib.parse import urlparse, urldefrag

from aiohttp import web, ClientSession
from fake_useragent import UserAgent

from scrapping.store import Store, build_path


def get_hostname(url):
    host = urlparse(url).hostname or ''  # .rstrip(':80').rstrip(':443')
    if host.count('.') > 1:
        parts = host.split('.')
        if parts[-2] == 'co':  # e.g. www.site.co.uk
            host = '.'.join(parts[-3:])
        else:
            host = '.'.join(parts[-2:])
    return host


class Entry:
    source: str
    url: str
    attempts: int

    def __init__(self, url, source=None):
        assert isinstance(url, str)
        url = urldefrag(url).url
        self.host = get_hostname(url)
        self.source = source or self.host
        self.url = url
        self.attempts = 0

    def __str__(self):
        return f"<Entry: {self.url}, errors: {self.attempts}>"


def build_dpid():
    dt = str(datetime.datetime.utcnow())
    return "{}/{}-{}".format(dt[:10], dt[11:19].replace(':', '_'), os.getpid())


def load_from_file(fpath: str):
    with open(fpath, 'r') as fin:
        urls = [line.strip() for line in fin]
    return urls


class Logger:
    ROTATION_TIME = 900

    def __init__(self, log_root):
        self.log_root = pathlib.Path(log_root)
        self.log_root.mkdir(parents=True, exist_ok=True)
        self.log_file = None
        self.log_started = time.time()

    def rotate_log(self):
        if self.log_file:
            self.log_file.close()
        log_fpath = self.log_root / build_dpid()
        log_fpath.parent.mkdir(parents=True, exist_ok=True)
        self.log_file = open(str(log_fpath) + '.csv', 'w', newline='')

    def log(self, entry: Entry, fpath: str, success: bool):
        if self.log_file is None or time.time() > self.log_started + self.ROTATION_TIME:
            self.rotate_log()
        status = 'OK' if success else 'Error'
        # fieldnames=["source", "URL", "status", "attempts", "fpath"])
        log_csv = csv.writer(self.log_file)
        log_csv.writerow((entry.source, entry.url, status, entry.attempts, fpath))
        del log_csv
        self.log_file.flush()


class Host:
    HOST_SLEEP_TIME = 1
    PAGE_CACHE_TIME = 86400 * 90  # 90 days

    def __init__(self, store, logger, host):
        self.host = host
        self.logger = logger
        self.store = store
        self.ua = UserAgent()
        self.uar = self.ua.random
        self.queue = []
        self.lock = asyncio.Lock()
        self.downloaded = set()

    async def fetch_url(self, entry: Entry, session: ClientSession):
        fpath = build_path(entry.url, 'html.gz')
        if self.store.exists(fpath, self.PAGE_CACHE_TIME):
            # print("Already downloaded", entry)
            self.downloaded.add(entry.url)
            return True
        # print("Downloading", entry)
        try:
            headers = {'User-Agent': self.uar}
            async with session.get(entry.url, headers=headers, timeout=30) as response:
                body = await response.read()
                base_url = str(response.url)
                # print(f"For {entry.url} base_url={base_url} type(body)={type(body)}")
                payload = base_url.encode('utf-8') + b'\n' + body

            self.store.save(fpath, payload)
            self.logger.log(entry, fpath, True)
            self.downloaded.add(fpath_base)

            if base_url != entry.url:
                # XXX: If the crawler was redirected to a new URL, save it under both old URL and new URL
                fpath_base = build_path(base_url, 'html.gz')
                if not self.store.exists(fpath_base, self.PAGE_CACHE_TIME):
                    self.store.save(fpath_base, payload)
                    self.downloaded.add(fpath_base)

            return True
        except Exception:
            # traceback.print_exc()
            self.logger.log(entry, fpath, False)
            return False

    async def fetch_host(self):
        queue = self.queue
        async with self.lock:
            async with ClientSession() as session:
                while queue:
                    entry = queue.pop(0)
                    success = await self.fetch_url(entry, session)
                    if not success:
                        if entry.attempts < 3:
                            entry.attempts += 1
                            queue.append(entry)
                        else:
                            self.store.save(build_path(entry.url, 'html.gz'), entry.url.encode('utf-8') + b'\n')
                    await asyncio.sleep(self.HOST_SLEEP_TIME)

    def enqueue(self, entry: Entry):
        if entry.url in self.downloaded or entry.url in self.queue:
            return False

        if self.store.exists(build_path(entry.url, 'html.gz')):
            self.downloaded.add(entry.url)
            return False

        self.queue.append(entry)
        if len(self.queue) == 1:
            # queue for this host was empty -- start new fetch_host
            loop = asyncio.get_event_loop()
            loop.create_task(self.fetch_host())
        return True

class AsyncDownloader:
    def __init__(self, store, logger):
        self.logger = logger
        self.store = store
        self.hosts = {}

    def enqueue(self, entry: Entry):
        host = entry.host
        if host not in self.hosts:
            self.hosts[host] = Host(self.store, self.logger, host)
        queue = self.hosts[host]
        # print("Enqueue", entry)
        return queue.enqueue(entry)

    def task_count(self):
        count = 0
        for h in self.hosts.values():
            if h.lock.locked():
                count += 1
        return count

    def queue_size(self):
        count = 0
        for h in self.hosts.values():
            count += len(h.queue)
        return count

    def total_size(self):
        count = 0
        for h in self.hosts.values():
            count += len(h.downloaded)
        return count

    def exists(self, entry):
        return self.store.exists(build_path(entry.url, 'html.gz'))


async def watch_file(path, downloader, interval):
    loaded = set()
    while True:
        total_added = 0
        for fn in sorted(os.listdir(path)):
            if not fn.startswith('feeds-'): continue
            if fn in loaded: continue
            loaded.add(fn)
            entries, new_entries = 0, 0
            for line in load_from_file(os.path.join(path, fn)):
                line = line.strip()
                if not line:
                    continue
                entry = Entry(line.strip())
                if not entry.host:
                    continue
                entries += 1
                new_entries += int(downloader.enqueue(entry))
            print(f"Found {entries}, added {new_entries} new entries from {fn}")
            total_added += new_entries
            if total_added >= 20000:
                break
        tc = downloader.task_count()
        qs = downloader.queue_size()
        ts = downloader.total_size()
        print(f"Downloading from {tc} hosts, queue size: {qs}, already downloaded: {ts}")
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
    parser.add_argument('--interval', type=int, default=10)
    parser.add_argument('--test-server', type=bool, default=False)

    return parser.parse_args()


if __name__ == "__main__":
    _args = _parse_args()
    main(_args)
