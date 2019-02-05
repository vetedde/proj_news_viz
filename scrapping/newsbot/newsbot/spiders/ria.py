import scrapy
from newsbot.items import Document
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit
from datetime import datetime


class RiaSpider(NewsSpider):
    name = 'ria'
    start_urls = ['https://www.ria.ru']
    config = NewsSpiderConfig(
        title_path='//h1[contains(@class, "article__title")]/text()',
        date_path='//div[contains(@class, "endless__item")]/@data-published',
        date_format='%Y-%m-%dT%H:%MZ',
        text_path='//div[contains(@class, "article__block") and @data-type = "text"]//text()',
        topics_path='//a[contains(@class, "article__tags-item")]/text()'
    )
    news_le = LinkExtractor(restrict_css='div.lenta__item')
    max_page_depth = 4

    def parse(self, response):
        article_links = self.news_le.extract_links(response)

        if response.meta.get('page_depth', 1) < self.max_page_depth:
            # Getting and forming the next page link
            next_page_link = response.xpath('//div[contains(@class, "lenta__item")]/@data-next').extract()[0]
            link_url = '{}{}'.format(self.start_urls[0], next_page_link)

            yield scrapy.Request(url=link_url,
                                 priority=100,
                                 callback=self.parse,
                                 meta={'page_depth': response.meta.get('page_depth', 1) + 1}
                                 )

        for link in article_links:
            yield scrapy.Request(url=link.url, callback=self.parse_document)

    def parse_document(self, response):
        for res in super().parse_document(response):
            # Leave only the last tag
            # (the last tag is always a global website tag)
            res['topics'] = [res['topics'][-1]]

            yield res
