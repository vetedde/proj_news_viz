from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy import Request, Selector
from datetime import datetime
from typing import List
from datetime import date


class RussiaTodaySpider(NewsSpider):
    name = 'rt'

    start_urls = ['https://russian.rt.com/sitemap.xml']

    config = NewsSpiderConfig(
        title_path='//h1[contains(@class, "article__heading")]/text()',
        subtitle_path= '_',
        date_path='//meta'
        '[contains(@name, "mediator_published_time")]/@content',
        date_format="%Y-%m-%dT%H:%M:%S",
        text_path='//div[contains(@class, "article__text") or contains(@class, "article__summary")]//text()',
        topics_path='//meta[contains(@name, "mediator_theme")]/@content',
        subtopics_path='//a[@data-trends-link=substring(//div[contains(@class, "layout__control-width")]/script, 50, 24)]//text()',
        authors_path='//meta[contains(@name, "mediator_author")]/@content',
        tags_path = '//a[contains(@rel, "tag")]//text()',
        reposts_fb_path='_',
        reposts_vk_path='_',
        reposts_ok_path='_',
        reposts_twi_path='_',
        reposts_lj_path='_',
        reposts_tg_path='_',
        likes_path='_',
        views_path='_',
        comm_count_path='_'
    )

    def parse(self, response):
        # Parse main sitemap
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()
        last_modif_dts = Selector(text=body).xpath('//lastmod/text()').getall()
        if self.start_date >= datetime.strptime(max(last_modif_dts).replace(':', ''), '%Y-%m-%d').date() >= self.until_date:
            for link, last_modif_dt in zip(links, last_modif_dts):
                # Convert last_modif_dt to datetime
                last_modif_dt = datetime.strptime(last_modif_dt.replace(':', ''), '%Y-%m-%d')

                if last_modif_dt.date() >= self.until_date and last_modif_dt.date() <= self.start_date:
                    yield Request(url=link, callback=self.parse_sub_sitemap, priority=1)

    def parse_sub_sitemap(self, response):
        # Parse sub sitemaps
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()
        last_modif_dts = Selector(text=body).xpath('//lastmod/text()').getall()
        if self.start_date >= datetime.strptime(max(last_modif_dts).replace(':', ''), '%Y-%m-%dT%H%M%S%z').date() >= self.until_date:
            for link, last_modif_dt in zip(links, last_modif_dts):
                # Convert last_modif_dt to datetime
                last_modif_dt = datetime.strptime(last_modif_dt.replace(':', ''), '%Y-%m-%dT%H%M%S%z')
                if self.start_date >= last_modif_dt.date() >= self.until_date:
                    yield Request(url=link, callback=self.parse_document, priority=100)

        '''def parse_articles_sitemap(self, response):
        # Parse sub sitemaps
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()
        last_modif_dts = Selector(text=body).xpath('//lastmod/text()').getall()
        print('gere', len(links))
        if self.start_date >= datetime.strptime(max(last_modif_dts).replace(':', ''), '%Y-%m-%dT%H%M%S%z').date() >= self.until_date:
            for link, last_modif_dt in zip(links, last_modif_dts):
                # Convert last_modif_dt to datetime
                last_modif_dt = datetime.strptime(last_modif_dt.replace(':', ''), '%Y-%m-%dT%H%M%S%z')

                if last_modif_dt.date() >= self.until_date and last_modif_dt.date() <= self.start_date:
                    if link.endswith('.shtml') and not link.endswith('index.shtml'):
                        yield Request(url=link, callback=self.parse_document, priority=1000)'''

    def _fix_syntax(self, sample: List[str], idx_split: int) -> List[str]:
        """Fix timestamp syntax, droping timezone postfix.
        """
        sample = [sample[0][:idx_split]]
        return sample

    def _get_date(self, lst: List[str]):
        """Convert list into date obj.
        """
        y, m, d = [int(num) for num in lst]
        return date(y, m, d)

    def parse_document(self, response):
        """Final parsing method.
        Parse each article."""
        for item in super().parse_document(response):
            # Try to drop timezone postfix.
            if 'tags' in item:
                item['tags'] = [tag.strip() for tag in item['tags'] if tag.strip()]
            if 'subtitle' in item:
                item['subtitle'] = [s.strip() for s in item['subtitle'] if s.strip()]
            try:
                item['date'] = self._fix_syntax(item['date'], -6)
            except KeyError:
                print('Error. No date value.')
            else:
                yield item
