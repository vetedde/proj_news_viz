import re
import os
import json
from datetime import datetime
from proj_news_viz.scrapping.validator.topic import process_topic

SOURCE_DIR = "./test_webhose"
DEST_DIR = "./sources/webh"
FILE_HEADER = 'datetime,url,section,topic,title,text\n'
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_REGEXP = "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
ALLOWED_METHODS = ['file', 'dir']


def datestring_to_date(datestring: str, date_format: str) -> datetime:
    """
    Brings the datestring to the right format
    :param datestring: unformatted datestring
    :param date_format: right date format
    :return: formatted datestring
    """
    return datetime.strptime(
        datestring,
        date_format
    )


def source_to_csv(source_file: str, dest_dir: str, encoding='utf8', save_method='file') -> None:
    """
    Creates file structure from source files
    :param source_file: path to source file
    :param dest_dir: the path to dir where to store resulted files
    :param encoding: files encoding
    :param save_method: defines how to store the data
    :return:
    """
    assert save_method in ALLOWED_METHODS, "Choose on of the following methods {}".format(ALLOWED_METHODS)
    file_content = json.load(open(source_file, encoding=encoding))
    file_date = datestring_to_date(
        re.search(DATE_REGEXP, file_content['published']).group(),
        DATE_FORMAT
    )
    if save_method == 'file':
        target_file = "{dest_dir}/{date}-{source}.csv".format(
            dest_dir=dest_dir,
            date=file_date.strftime("%Y-%m"),
            source=file_content['thread']['site']
        )
    elif save_method == 'dir':
        target_dir = "{dest_dir}/{year}/{month}".format(
                dest_dir=dest_dir,
                year=file_date.strftime("%Y"),
                month=file_date.strftime("%-m")
        )
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        target_file = "{target_dir}/{source}.csv".format(
            target_dir=target_dir,
            source=file_content['thread']['site']
        )
    payload = {
        "datetime": str(int(file_date.timestamp())),
        "url": file_content['url'],
        "section": file_content['thread']['section_title'],
        "topic": process_topic(file_content['url']),
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
