import scrapy
from newsbot.items import Document
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit
from datetime import datetime


class GazetaSpider(NewsSpider):
    name = 'gazeta'
    start_urls = ['https://www.gazeta.ru/news/']
    config = NewsSpiderConfig(
        title_path='//h1/text()',
        date_path='//time[contains(@class, "date_time red")]/text()',
        date_format='%d.%m.%Y | %H:%M',
        text_path='//div[contains(@class, "article-text-body")]//text()',
        topics_path='//div[contains(@class, "active")]/a/span/text()'
    )
    news_le = LinkExtractor(restrict_css='div.article_text h1.txt_2b')
    max_page_depth = 4

    def parse(self, response):
        if response.meta.get('page_depth', 1) < self.max_page_depth:
            # Get last article datetime on the current page
            last_page_dt = response.xpath('//time[contains(@class, "txtclear")]/@datetime').extract()[-1]
            # Convert it to datetime without timezone part
            last_page_dt = datetime.strptime(last_page_dt[:-6], '%Y-%m-%dT%H:%M:%S')

            # Forming the next page link
            link_url = '{}?p=page&d={}'.format(self.start_urls[0], last_page_dt.strftime('%d.%m.%Y_%H:%M'))

            yield scrapy.Request(url=link_url,
                                 priority=100,
                                 callback=self.parse,
                                 meta={'page_depth': response.meta.get('page_depth', 1) + 1}
                                 )

        for link in self.news_le.extract_links(response):
            yield scrapy.Request(url=link.url, callback=self.parse_document)

    def parse_document(self, response):
        for res in super().parse_document(response):
            # Remove advertisement blocks
            ad_parts = ('\nРеклама\n', '\n.AdCentre_new_adv', ' AdfProxy.ssp', '\nset_resizeblock_handler')

            res['text'] = [x for x in res['text'] if x != '\n' and not x.startswith(ad_parts)]

            yield res
