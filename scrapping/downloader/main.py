"""
Async downloader
"""
import argparse
from aiohttp import ClientSession
import asyncio
from datetime import datetime
import gzip
import os
import logging
import hashlib

logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s][%(levelname)-5.5s] %(message)s",
    handlers=[
        logging.FileHandler("/tmp/{:%Y-%m-%d}.log".format(datetime.now())),
        logging.StreamHandler()
    ],
    level=logging.DEBUG
)
visited = set()


def hashit(s):
    return hashlib.md5(s.encode()).hexdigest()


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str,
                        default='data/parser/lists/files_to_download.txt')
    parser.add_argument('--output', type=str,
                        default='data/parser/downloaded/')
    parser.add_argument('--interval', type=int, default=60)

    return parser.parse_args()


async def fetch(url, session, outpath):
    try:
        async with session.get(url) as response:
            body = await response.read()
            with gzip.open(outpath, 'w') as fout:
                fout.write(body)
                logging.info('{} success {}'.format(url, outpath))
    # todo: specify exceptions
    except:  # noqa: E722
        logging.error('{} error'.format(url))


async def watch_for_tasks(path, out_folder, interval=60):
    async with ClientSession() as session:
        while True:
            # let's break this loop in case of errors.
            with open(path, 'r') as fin:
                urls = [line.strip() for line in fin.readlines()]

            tasks = []
            for url in urls:
                # todo: check url without request
                if len(url) == 0:  # just avoid empty lines in input file
                    continue
                url_hash = hashit(url)
                if url_hash in visited:
                    continue
                visited.add(url_hash)
                # todo: group by servername, add rate-limitter
                out_path = os.path.join(out_folder, url_hash + '.html.gz')
                tasks.append(fetch(url, session, out_path))
            if len(tasks) > 0:
                await asyncio.wait(tasks)

            logging.info('Done')
            # tbd: move to aionotify or a full-feature service architecture
            await asyncio.sleep(interval)


def main(args):
    os.makedirs(args.output, exist_ok=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        watch_for_tasks(args.input, args.output, interval=args.interval))


if __name__ == "__main__":
    args = _parse_args()
    main(args)
