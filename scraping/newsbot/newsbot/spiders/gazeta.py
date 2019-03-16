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
        date_path='//time[contains(@class, "date_time red")]/@datetime',
        date_format='%Y-%m-%dT%H:%M:%S%z',
        text_path='//div[contains(@class, "article-text-body")]//text()',
        topics_path='//div[contains(@class, "active")]/a/span/text()'
    )
    news_le = LinkExtractor(restrict_css='div.article_text h1.txt_2b')
    main_pub_d_xpath = '//time[contains(@class, "txtclear numb_b")]/@datetime'

    def parse(self, response):
        for link in self.news_le.extract_links(response):
            yield scrapy.Request(url=link.url, callback=self.parse_document)

        # Get the last article date on this page
        last_pub_dt = self._get_last_pub_dt(response)

        # Determine if this is the last page
        if last_pub_dt.date() >= self.until_date:
            # # Get last article datetime on the current page
            # last_page_dt = response.xpath('//time[contains(@class, "txtclear")]/@datetime').extract()[-1]
            # # Convert it to datetime without timezone part
            # last_page_dt = datetime.strptime(last_page_dt[:-6], '%Y-%m-%dT%H:%M:%S')

            # Forming the next page link
            link_url = '{}?p=page&d={}'.format(self.start_urls[0], last_pub_dt.strftime('%d.%m.%Y_%H:%M'))

            yield scrapy.Request(url=link_url,
                                 priority=100,
                                 callback=self.parse,
                                 meta={'page_depth': response.meta.get('page_depth', 1) + 1}
                                 )

    def parse_document(self, response):
        for res in super().parse_document(response):
            # Remove advertisement blocks
            ad_parts = ('\nРеклама\n', '\n.AdCentre_new_adv', ' AdfProxy.ssp', '\nset_resizeblock_handler')

            res['text'] = [x for x in res['text'] if x != '\n' and not x.startswith(ad_parts)]

            # Remove ":" in timezone
            pub_dt = res['date'][0]
            res['date'] = [pub_dt[:-3] + pub_dt[-3:].replace(':', '')]

            yield res

    def _get_last_pub_dt(self, response):
        # Get the last page in the page to see, whether we need another page
        pub_dts = response.xpath(self.main_pub_d_xpath).extract()

        last_date = list(pub_dts)[-1]
        last_date = last_date[:-3] + last_date[-3:].replace(':', '')  # remove ":" for timezone correct parsing
        last_date = datetime.strptime(last_date, self.config.date_format)

        return last_date
