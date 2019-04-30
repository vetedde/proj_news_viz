import scrapy
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor
from datetime import datetime


class GazetaSpider(NewsSpider):
    name = 'gazeta'
    start_urls = ['https://www.gazeta.ru/sitemap.shtml']
    config = NewsSpiderConfig(
        title_path='//h1/text()',
        date_path='//time[contains(@itemprop, "datePublished")]/@datetime',
        date_format='%Y-%m-%dT%H:%M:%S%z',
        text_path='//div[contains(@itemprop, "articleBody")]//p//text() | '
                  '//span[contains(@itemprop, "description")]//text()',
        topics_path='//div[contains(@class, "active")]/a/span/text()',
        authors_path='//span[contains(@itemprop, "author")]//text()'
    )
    sitemap_le = LinkExtractor(restrict_xpaths='//div[contains(@class, "sitemap_list")]/ul/ul')
    articles_le = LinkExtractor(restrict_xpaths='//h2[contains(@itemprop, "headline")]')
    news_le = LinkExtractor(restrict_css='div.article_text h1.txt_2b')

    def parse(self, response):
        for link in self.sitemap_le.extract_links(response):
            yield scrapy.Request(url=link.url, callback=self.parse_page)

    def parse_page(self, response):
        if 'news' in response.url:
            links = self.news_le.extract_links(response)
        else:
            links = self.articles_le.extract_links(response)

        pub_dts = response.xpath(self.config.date_path).extract()
        for pub_dt, link in zip(pub_dts, links):
            pub_dt = pub_dt[:-3] + pub_dt[-3:].replace(':', '')  # remove ":" for timezone correct parsing
            pub_dt = datetime.strptime(pub_dt, self.config.date_format)

            if pub_dt.date() >= self.until_date:
                yield scrapy.Request(url=link.url, callback=self.parse_document)

        # Determine if this is the last page
        if pub_dt.date() >= self.until_date:
            # Forming the next page link
            link_url = '{}?p=page&d={}'.format(self.start_urls[0], pub_dt.strftime('%d.%m.%Y_%H:%M'))

            yield scrapy.Request(url=link_url,
                                 priority=100,
                                 callback=self.parse,
                                 meta={'page_depth': response.meta.get('page_depth', 1) + 1}
                                 )

    def parse_document(self, response):
        for res in super().parse_document(response):
            # Remove advertisement blocks
            ad_parts = ('\nРеклама\n', '\n.AdCentre_new_adv', ' AdfProxy.ssp', '\nset_resizeblock_handler')

            res['text'] = [x.replace('\n', '\\n') for x in res['text'] if x != '\n' and not x.startswith(ad_parts)]

            # Remove ":" in timezone
            pub_dt = res['date'][0]
            res['date'] = [pub_dt[:-3] + pub_dt[-3:].replace(':', '')]

            yield res
