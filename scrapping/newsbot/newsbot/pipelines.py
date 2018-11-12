# -*- coding: utf-8 -*-

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime

class NewsbotPipeline(object):
    def open_spider(self, spider):
        self.file = open(spider.name + '.csv', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        item["title"] = spider.process_title(item["title"][0])
        item["topics"] = item["topics"][0]
        item["edition"] = item["edition"][0]
        item["url"] = item["url"][0]
        item["text"] = spider.process_text(item["text"])
        date = datetime.datetime.strptime(item["date"][0], spider.config.date_format)
        item["date"] = date.strftime("%Y-%m-%d %H:%M:%S")
        line = (item["date"], item["url"], item["edition"], '"' + item["topics"] + '"',
            '"' + item["title"] + '"', '"' + item["text"] + '"' + '\n')
        line = ",".join(line)
        self.file.write(line)
        return item
