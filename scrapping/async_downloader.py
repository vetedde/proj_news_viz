from aiohttp import ClientSession, TCPConnector
import asyncio
from pypeln import TaskPool
import hashlib
import gzip
import os
import datetime

limit = 100
PID = '1'
FILE_NAME = 'files_to_download.txt'
CONF_FOLDER = 'async/data/parser/conf/'
ARTICLES_FOLDER = 'async/data/parser/articles/'
INPUT_FOLDER = 'async/data/parser/lists/'
LOG_FOLDER = 'async/data/parser/downloaded/'

SAVED_FILES = set()


async def fetch(url, session):
    urlhashname = hashlib.md5(url.encode()).hexdigest()
    if urlhashname not in SAVED_FILES and os.path.exists(ARTICLES_FOLDER + urlhashname) is False:
        status = 'success_200'
        try:
            async with session.get(url) as response:
                body = await response.read()
                urlhashname = hashlib.md5(url.encode()).hexdigest()
                with gzip.open(ARTICLES_FOLDER + urlhashname + '.html.gz', 'w') as file:
                    file.write(body)
                SAVED_FILES.add(urlhashname)
                await asyncio.sleep(1)
        except Exception:
            status = 'error' + str(response.status)
            urlhashname = 'None'

        LogFile.write('{};{};{};{}{}'.format(url, status, urlhashname, ARTICLES_FOLDER, '\n'))


async def _main(urls):
    connector = TCPConnector(limit=None)
    total_requests = len(urls)
    async with ClientSession(connector=connector) as session, TaskPool(limit) as tasks:
        for i in range(total_requests):
            await tasks.put(fetch(urls[i], session))
    # os.remove(INPUT_FOLDER+FILE_NAME)
    print('Done')


# Функция проверки нового файла загрузки и добавдение ссылок в задание
async def addurls():
    print("h")
    while True:
        try:
            with open(INPUT_FOLDER + FILE_NAME, 'r') as file:
                urls = file.readlines()
            urls = [line.rstrip() for line in urls]
            loop.create_task(_main(urls))
        except Exception:
            pass
        await asyncio.sleep(60)
        await addurls()


def main():
    CURRENT_DATE = str(datetime.date.today())  # текущая дата для создания папки с логом
    if not os.path.exists(LOG_FOLDER + CURRENT_DATE):  # создаем папку с текущей датой для записи файла лога
        os.makedirs(LOG_FOLDER + CURRENT_DATE)
    CURRENT_TIME = str(datetime.datetime.now().time())[:8].replace(':', '-')

    with open(LOG_FOLDER + CURRENT_DATE + '/' + CURRENT_TIME + '_' + PID + '.csv', 'w') as LogFile:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(addurls())
        # loop.run_forever()


if __name__ == "__main__":
    main()
