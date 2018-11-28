import datetime
import scrapy
from newsbot.items import Document
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit


class GazetaSpider(NewsSpider):
    name = "gazeta"
    start_urls = ["https://www.gazeta.ru/news/"]
    config = NewsSpiderConfig(
        title_path='//h1/text()',
        date_path='//time[contains(@class, "date_time red")]/text()',
        date_format="%d.%m.%Y | %H:%M",
        text_path='//div[contains(@class, "article-text-body")]//text()',
        topics_path='//div[contains(@class, "active")]/a/span/text()'
    )
    news_le = LinkExtractor(restrict_css='div.article_text h1.txt_2b')
    page_le = LinkExtractor(restrict_xpaths='.//div[@id="other_click"]/a[1]')
    max_page_depth = 4

    def parse(self, response):
        if response.meta.get("page_depth", 1) < self.max_page_depth:
            for link in self.page_le.extract_links(response):
                link.url = '{}?p=page&d={}'.format(self.start_urls[0], link.url[-16:].replace(' ', '_'))
                yield scrapy.Request(url=link.url,
                                     priority=100,
                                     callback=self.parse,
                                     headers={'referer': '{}?updated'.format(self.start_urls[0])},
                                     meta={"page_depth": response.meta.get("page_depth", 1) + 1}
                                     )

        for link in self.news_le.extract_links(response):
            yield scrapy.Request(url=link.url, callback=self.parse_document)

    def parse_document(self, response):
        for res in super().parse_document(response):
            # Remove advertisement blocks
            ad_parts = ('\nРеклама\n', '\n.AdCentre_new_adv', ' AdfProxy.ssp', '\nset_resizeblock_handler')

            res["text"] = [x for x in res["text"] if x != '\n' and not x.startswith(ad_parts)]

            yield res
