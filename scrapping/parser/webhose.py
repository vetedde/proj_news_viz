import re
import os
import json
from datetime import datetime

SOURCE_DIR = "./webhose.io-news-ru/"
DEST_DIR = "./sources/files"
FILE_HEADER = 'datetime,url,topic,title,text\n'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_REGEXP = "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"


def datestring_to_date(datestring, date_format):
    return datetime.strptime(
        datestring,
        date_format
    )


def source_to_csv(source_file, dest_dir, encoding='utf8'):
    file_content = json.load(open(source_file, encoding=encoding))
    file_date = datestring_to_date(
        re.search(DATE_REGEXP, file_content['published']).group(),
        DATE_FORMAT
    )
    target_file = "{desc_dir}/{date}-{source}.csv".format(
        desc_dir=dest_dir,
        date=file_date.strftime("%Y-%m"),
        source=file_content['thread']['site']
    )
    payload = {
        "datetime": str(int(file_date.timestamp())),
        "url": file_content['url'],
        "topic": file_content['thread']['section_title'],
        "title": file_content['title'],
        "text": re.sub(r'(\n|\t|,)', '', file_content['text'])
    }
    if not os.path.exists(target_file):
        with open(target_file, 'w', encoding=encoding) as f:
            f.write(FILE_HEADER)
    with open(target_file, 'a', encoding=encoding) as f:
        f.write(
            ','.join(payload.values()) + '\n'
        )


if __name__ == '__main__':
    files = ["{}/{}".format(SOURCE_DIR, file_name) for file_name in os.listdir(SOURCE_DIR)]
    for target_file in files:
        source_to_csv(target_file, DEST_DIR, encoding='koi8-r')
