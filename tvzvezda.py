from datetime import datetime
import scrapy
from newsbot.items import Document
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit
from urllib.parse import urljoin


class TvZvezdaSpider(NewsSpider):
    name = "tvzvezda"
    start_urls = ["https://tvzvezda.ru/news"]
    config = NewsSpiderConfig(
        title_path='//h1/text()',
        date_path='//div[contains(@class, "date_news")]//text()',
        #date_format="%Y-%m-%dT%H:%M:%S",
	date_format="%H:%M %d.%m.%Y",
        text_path='//div[contains(@class, "glav_text")]//text()',
        topics_path='//meta[contains(@property, "article:section")]/@content'
    )
    news_le = LinkExtractor(restrict_css='div.js-ajax-receiver a.news_one')
   # page_le = LinkExtractor(restrict_css='a.all_news js-ajax-call')
    
  
    z=0
    visited_urls = []




    def parse(self, response):
        link2="https://tvzvezda.ru/"
        
        if response.url not in self.visited_urls:
            for link in self.news_le.extract_links(response):
              
                yield scrapy.Request(url=link.url, callback=self.parse_document)
        next_pages = response.xpath('//a[contains(@class, "all_news js-ajax-call")]/@href').extract()
        next_pages=next_pages[-1]
        new_url='20/'+str(self.z)+'/?_=1542171175300'
        more = urljoin(link2,next_pages+new_url)
        self.z+=20
        
        yield response.follow(more, callback=self.parse)
        
    def parse_document(self, response):
        for res in super().parse_document(response):
            yield res
            
            
            
            
            
            
            
            
            