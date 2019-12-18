import os
import time
from datetime import datetime

import luigi
from luigi.contrib.postgres import PostgresTarget
from luigi.format import UTF8

from razdel import tokenize
from razdel import sentenize

from uuid import uuid4
import configparser

# Коннектор к базе данных
from dbconnector import UseDatabase


class WriteDataToDatabase(luigi.Task):
    """
    Функция ищет строки в таблице raw_data.raw_data,
    которые еще не были записаны в таблицу prepared_data.news
    обрабатывает их и затем вставляет в таблицу prepared_data.news
    """
    run_date = luigi.DateParameter(default=datetime.now().date())
    config = configparser.ConfigParser()
    config.read('db.ini')

    dbconfig = {'host': config['dev']['host'],
                'dbname': config['dev']['db'],
                'user': config['dev']['user'],
                'password': config['dev']['password']}

    def get_tokens(self, sentence):
        for news in sentence:
            if len(news) > 0:
                yield [
                    _.text for _ in list(tokenize(news))
                ]

    def run(self):
        with UseDatabase(self.dbconfig) as cursor:
            sql = "SELECT id_raw_data, id_news_source, date, url, title, text FROM raw_data.raw_data where batch_date = '1900-01-01 00:00:00' "

            cursor.execute(sql)
            query_results = cursor.fetchall()

            sql = """INSERT INTO prepared_data.news
                     (id_news, id_topic, id_news_source, id_author, date_news, link_news, title, text_news, created_date, modified_date, batch_date)
                     VALUES 
                     (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            dt_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for line in query_results:

                sents = list(sentenize(line[5]))
                sentence = [_.text for _ in sents]

                cursor.execute(sql, (
                    line[0],
                    line[1],
                    '4847c8c7-a14f-4d59-8f62-a1c622db4aab',
                    '4847c8c7-a14f-4d59-8f62-a1c622db4aab',
                    line[2],
                    line[3],
                    line[4],
                    str(list(self.get_tokens(sentence))),
                    dt_now,
                    dt_now,
                    '1900-01-01 00:00:00'))
            self.get_target().touch()

    def get_target(self):
        return PostgresTarget(host=self.config['dev']['host'],
                              database=self.config['dev']['db'],
                              user=self.config['dev']['user'],
                              password=self.config['dev']['password'],
                              table='prepared_data.news',
                              update_id=str(self.run_date))

    def output(self):
        return self.get_target()


# python preprocess.py UpdateBatchDate --local-scheduler
class UpdateBatchDate(luigi.Task):
    """
    Функция обновляется поле batch_date в таблице raw_data.raw_data
    для тех строк, которые были записаны в таблицу prepared_data.news.
    Зависит от выполнения WriteDataToDatabase
    """
    config = configparser.ConfigParser()
    config.read('db.ini')

    dbconfig = {'host': config['dev']['host'],
                'dbname': config['dev']['db'],
                'user': config['dev']['user'],
                'password': config['dev']['password']}

    def requires(self):
        return WriteDataToDatabase()

    def run(self):
        with UseDatabase(self.dbconfig) as cursor:
            batch_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            sql = """UPDATE raw_data.raw_data
                     SET batch_date= %s
                     WHERE raw_data.raw_data.id_raw_data in (
                     select prepared_data.news.id_news
                     from prepared_data.news
                     where prepared_data.news.batch_date = '1900-01-01 00:00:00');"""

            cursor.execute(sql, (batch_date,))


class Dbwriter(object):
    """
    Обертывает класс CSVCorpusReader, читает подготовленные файлы для загрузки
    и записывает данные в БД в таблицу сырых данных
    """
    def __init__(self, corpus):
        """
        corpus - класс CSVCorpusReader
        """
        self.corpus = corpus

    def __get_fileids(self, fileids=None, categories=None):
        fileids = self.corpus.check_arguments(fileids, categories)
        if fileids:
            return fileids
        return self.corpus.fileids()

    def __process(self, fileid):
        """
        Вызывается для файла и записывает данные из него в БД.
        """

        # получить название источника данных
        news_source = os.path.dirname(fileid)
        print(news_source)

        # database connect
        config = configparser.ConfigParser()
        config.read('db.ini')

        dbconfig = {'host': config['dev']['host'],
                    'dbname': config['dev']['db'],
                    'user': config['dev']['user'],
                    'password': config['dev']['password']}

        n_rows = 0
        started = time.time()
        with UseDatabase(dbconfig) as cursor:
            sql = "SELECT * FROM raw_data.news_source WHERE name= %s"

            cursor.execute(sql, (news_source, ))
            query_results = cursor.fetchall()

            sql = """INSERT INTO raw_data.raw_data
                     (id_raw_data, id_news_source, date, url, edition, topics, authors, title, text, reposts_fb, reposts_vk, reposts_ok, reposts_twi, reposts_lj, reposts_tg, likes, views, comm_count, created_date, modified_date, batch_date)
                     VALUES
                     (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            for line in list(self.corpus.read_docs(fileid)):
                n_rows = n_rows + 1
                cursor.execute(sql, (uuid4().hex, query_results[0][0], line['date'], line['url'], line['edition'], line['topics'], line['authors'], line['title'], line['text'], line['reposts_fb'], line['reposts_vk'], line['reposts_ok'], line['reposts_twi'], line['reposts_lj'], line['reposts_tg'], line['likes'], line['views'], line['comm_count'], '2019-12-02 22:43:00', '2019-12-02 22:43:00', '1900-01-01 00:00:00'))

        print('Количество строк в файле ' + fileid + ':', n_rows)
        print('Время обработки в секундах: ' + str(time.time() - started))
        return fileid + ' is done'

    def write_file(self, fileids=None, categories=None):
        # Получить имена файлов для обработки
        return [
            self.__process(fileid) for fileid in self.__get_fileids(fileids, categories)
        ]


if __name__ == '__main__':
    luigi.run()
