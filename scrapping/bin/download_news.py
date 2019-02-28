import argparse
import asyncio
import csv
import random
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urldefrag

from aiohttp import web, ClientSession
from fake_useragent import UserAgent

from scrapping.uniscrape.links import LinksFolder
from scrapping.uniscrape.sites import get_sites
from scrapping.uniscrape.store import PageStore, FileStore, get_hostname, Page, RobotsParser, build_dpid, get_sitename

PAGE_CACHE_TIME = 86400 * 365 * 100  # 100 years
BAD_EXT = frozenset(['jpg', 'jpeg', 'png', 'gif', 'ico', 'mp3', 'wmv', 'wma', 'mp4', 'webp', 'flv', 'css', 'js'])
SOURCES = 'data/parser/conf/sources.csv'
ALLOWED_SITES = set(get_sitename(url) for name, url in get_sites(SOURCES))


class Entry:
    source: str
    url: str
    attempts: int
    downloaded: bool

    def __init__(self, url, source=None):
        assert isinstance(url, str)
        url = urldefrag(url).url
        self.host = get_hostname(url)
        self.source = source or self.host
        self.url = url
        self.attempts = 0
        self.downloaded = False

    def __str__(self):
        return f"<Entry: {self.url}, errors: {self.attempts}>"


class Logger:
    ROTATION_TIME = 900

    def __init__(self, log_root):
        self.log_root = Path(log_root)
        self.log_root.mkdir(parents=True, exist_ok=True)
        self.log_file = None
        self.log_started = time.time()

    def rotate_log(self):
        if self.log_file:
            self.log_file.close()
        log_fpath = self.log_root / build_dpid().replace('-', '/', 1)
        log_fpath.parent.mkdir(parents=True, exist_ok=True)
        self.log_file = open(str(log_fpath) + '.csv', 'w', newline='')

    def log(self, entry: Entry, status: str):
        if self.log_file is None or time.time() > self.log_started + self.ROTATION_TIME:
            self.rotate_log()
        # fieldnames=["URL", "status"])
        log_csv = csv.writer(self.log_file)
        log_csv.writerow((entry.url, status))
        del log_csv
        self.log_file.flush()


class Host:
    HOST_SLEEP_TIME = 1

    def __init__(self, store, logger, host):
        self.host = host
        self.logger = logger
        self.store = store
        self.ua = UserAgent()
        self.uar = self.ua.random
        self.queue = []
        self.lock = asyncio.Lock()
        self.urls = set()
        self.downloaded = 0
        self.robots = RobotsParser(store)

    def can_fetch(self, url):
        if url.startswith('https://www.kommersant.ru/doc/'):
            return True
        return self.robots.can_fetch(url)

    async def fetch_url(self, entry: Entry, session: ClientSession):
        if self.store.exists(entry.url):
            return 'exists'
        try:
            if not self.can_fetch(entry.url):
                entry.attempts = 2
                return 'forbidden'
            headers = {'User-Agent': self.uar}
            async with session.get(entry.url, headers=headers, timeout=30) as response:
                body = await response.read()
                page = Page(str(response.url), body)
            self.store.save_page(entry.url, page)
            self.urls.add(page.url)
            return 'success'
        except Exception as e:
            print(f"Downloading {entry.url} and got exception {type(e)}: {str(e)}")
            import traceback
            traceback.print_exc()
            return 'error'

    async def fetch_host(self):
        queue = self.queue
        async with self.lock:
            async with ClientSession() as session:
                while queue:
                    entry = queue.pop(0)
                    status = await self.fetch_url(entry, session)
                    if status == 'success':
                        self.logger.log(entry, 'OK')
                        self.downloaded += 1
                    elif status == 'exists':
                        print(f"Already exists: {entry.url}")
                        # already downloaded
                        pass
                    elif status == 'forbidden':
                        print(f"Forbidden by robots.txt: {entry.url}")
                        self.logger.log(entry, 'forbidden')
                    elif status == 'error':
                        if entry.attempts < 2:
                            entry.attempts += 1
                            print(f"Failed to download {entry.attempts} times: {entry.url}")
                            queue.append(entry)
                        else:
                            # save empty doc
                            print(f"Failed to download after 3 attempts: {entry.url}")
                            self.logger.log(entry, 'failed')
                            self.store.save_page(entry.url, Page(entry.url, b''))
                    else:
                        raise Exception(f"Can't handle status {status}")
                    if status in ['success', 'error']:
                        await asyncio.sleep(self.HOST_SLEEP_TIME)

    def enqueue(self, entry: Entry):
        fn = entry.url.split('/')[-1]
        if '.' in fn:
            ext = fn.split('.')[-1].lower()
            if ext in BAD_EXT:
                return False

        if entry.url in self.urls:
            return False
        self.urls.add(entry.url)

        if self.store.exists(entry.url):
            return False
        self.queue.append(entry)
        if len(self.queue) == 1:
            # queue for this host was empty -- start new fetch_host
            asyncio.get_event_loop().create_task(self.fetch_host())
        return True


class AsyncDownloader:
    def __init__(self, store: PageStore, logger: Logger):
        self.logger = logger
        self.store = store
        self.hosts = {}

    def enqueue(self, entry: Entry):
        host = entry.host
        if host not in self.hosts:
            self.hosts[host] = Host(self.store, self.logger, host)
        queue = self.hosts[host]
        return queue.enqueue(entry)

    def active_hosts(self):
        return {name: h for name, h in self.hosts.items() if h.lock.locked()}

    def print_stats(self):
        active = self.active_hosts()
        queue_size = sum([len(host.queue) for name, host in active.items()])
        downloads = sum([h.downloaded for h in self.hosts.values()])
        total_urls = sum([len(h.urls) for h in self.hosts.values()])
        print(f"Downloading from {len(active)} hosts, queue size: {queue_size}, " +
              f"downloaded: {downloads}, total: {total_urls}")
        top_queued = Counter({name: len(host.queue) for name, host in active.items()})
        if top_queued:
            print("Top hosts:")
            for name, count in top_queued.most_common(5):
                downloaded = self.hosts[name].downloaded
                total = count + downloaded
                print(f"{name}: {downloaded} / {total}")


async def watch_file(lists_dir: Path, downloader, interval):
    files = LinksFolder(lists_dir)
    while True:
        total_added = 0
        total_found = 0
        for path_fn, links in files.load_files():
            entries, new_entries = 0, 0
            for line in links:
                if not line:
                    continue
                if get_sitename(line) not in ALLOWED_SITES:
                    continue
                entry = Entry(line)
                if not entry.host:
                    continue
                entries += 1
                new_entries += int(downloader.enqueue(entry))
            print(
                f"Found {entries:5d} entries, added {new_entries:3d} new entries from {path_fn.parent.name}/{path_fn.name}")
            total_found += entries
            total_added += new_entries
            if total_added >= 10000:
                break
            if total_found >= 100000:
                break
        downloader.print_stats()
        await asyncio.sleep(interval)


def run_test_server():
    async def handle(request):
        await asyncio.sleep(random.randint(0, 3))
        return web.Response(text="Hello, World!")

    app = web.Application()
    app.router.add_route('GET', '/{name}', handle)
    web.run_app(app)


def main(args):
    store = PageStore(FileStore(args.download_dir), PAGE_CACHE_TIME)
    logger = Logger(args.log_dir)
    downloader = AsyncDownloader(store, logger)

    loop = asyncio.get_event_loop()

    if args.test_server:
        run_test_server()

    watchdog = watch_file(Path(args.input_dir),
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
    parser.add_argument('--interval', type=int, default=1)
    parser.add_argument('--test-server', type=bool, default=False)

    return parser.parse_args()


if __name__ == "__main__":
    _args = _parse_args()
    main(_args)
