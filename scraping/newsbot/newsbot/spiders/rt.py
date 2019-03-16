import datetime
import scrapy
from newsbot.items import Document
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit


class RussiaTodaySpider(NewsSpider):
    name = "rt"
    start_urls = ["https://russian.rt.com/news"]
    config = NewsSpiderConfig(
        title_path='//h1/text()',
        date_path='//meta[contains(@name, "mediator_published_time")]/@content',
        date_format="%Y-%m-%dT%H:%M:%S",
        text_path='//div[contains(@class, "article__text")]//text()',
        topics_path='//meta[contains(@name, "mediator_theme")]/@content'
    )
    news_le = LinkExtractor(restrict_css='div.listing__card div.card__heading')
    page_le = LinkExtractor(restrict_css='div.listing__button.listing__button_js',
                            tags=['div'], attrs=['data-href'])
    max_page_depth = 4

    def parse(self, response):
        if response.meta.get("page_depth", 1) < self.max_page_depth:
            for link in self.page_le.extract_links(response):
                yield scrapy.Request(url=link.url,
                                     priority=100,
                                     callback=self.parse,
                                     meta={"page_depth": response.meta.get("page_depth", 1) + 1}
                                     )

        for link in self.news_le.extract_links(response):
            yield scrapy.Request(url=link.url, callback=self.parse_document)

    def parse_document(self, response):
        for res in super().parse_document(response):
            if isinstance(res, Document):
                if isinstance(res["date"], list):
                    res["date"] = [x[:-6] for x in res["date"] if x]
                else:
                    res["date"] = res["date"][:-6]
            yield res
