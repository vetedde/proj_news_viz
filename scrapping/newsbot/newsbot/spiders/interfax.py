import datetime

import scrapy
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig


class InterfaxSpider(NewsSpider):
    name = "interfax"
    start_urls = ["https://www.interfax.ru/news/2008/02/11"]
    config = NewsSpiderConfig(
        title_path='//h1/text()',
        date_path='//div[contains(@class, "tMC_head")]/meta[contains(@itemprop, "datePublished")]/@content',
        date_format="%Y-%m-%dT%H:%M:%S",
        text_path='//article//text()',
        topics_path='//div[contains(@class, "textML")]/a/text()'
    )

    def parse(self, response):
        today = datetime.datetime.today()
        first_day = datetime.datetime(year=2008, month=2, day=11)
        date_range = [first_day + datetime.timedelta(days=x) for x in range((today-first_day).days)]
        for date in date_range:
            url = "https://www.interfax.ru/news/" + date.strftime("%Y/%m/%d")
            yield response.follow(url, self.parse_page)

    def parse_page(self, response):
        url = response.url
        page = int(url.split("page_")[-1]) if "page_" in url else 0
        for page_href in response.xpath('//div[contains(@class, "pages")]/a/@href').extract():
            if page != 0:
                continue
            yield response.follow(page_href, self.parse_page)
        for document_href in response.xpath('//div[contains(@class, "an")]/div/a/@href').extract():
            yield response.follow(document_href, self.parse_document)

