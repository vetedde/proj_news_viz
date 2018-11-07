from urllib.parse import urlsplit

import scrapy
from scrapy.loader import ItemLoader

from newsbot.items import Document


class NewsSpiderConfig:
    def __init__(self, title_path, date_path, date_format, text_path, topics_path):
        self.title_path = title_path
        self.date_path = date_path
        self.date_format = date_format
        self.text_path = text_path
        self.topics_path = topics_path


class NewsSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        assert self.config
        assert self.config.title_path
        assert self.config.date_path
        assert self.config.date_format
        assert self.config.text_path
        assert self.config.topics_path
        super().__init__(*args, **kwargs)

    def parse_document(self, response):
        url = response.url
        base_edition = urlsplit(self.start_urls[0])[1]
        edition = urlsplit(url)[1]

        l = ItemLoader(item=Document(), response=response)
        l.add_value('url', url)
        l.add_value('edition', '-' if edition == base_edition else edition)
        l.add_xpath('title', self.config.title_path)
        l.add_xpath('date', self.config.date_path)
        l.add_xpath('text', self.config.text_path)
        l.add_xpath('topics', self.config.topics_path)
        yield l.load_item()

    def process_title(self, title):
        title = title.replace('"', '\\"')
        return title

    def process_text(self, paragraphs):
        text = "\\n".join([p.strip() for p in paragraphs if p.strip()])
        text = text.replace('"', '\\"')
        return text

