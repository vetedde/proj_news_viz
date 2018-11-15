from datetime import datetime
import scrapy
from newsbot.items import Document
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit
from urllib.parse import urljoin


class IzSpider(NewsSpider):
    name = "iz"
    start_urls = ["https://iz.ru/feed"]
    config = NewsSpiderConfig(
        title_path='//h1/span/text()',
        date_path='//div[contains(@class, "article_page__left__top__time__label")]/div/time/@datetime',
        date_format="%Y-%m-%dT%H:%M:%SZ",
	text_path='//div[contains(@itemprop, "articleBody")]/div/p//text()',
        topics_path='//div[contains(@class, "rubrics_btn")]/div/a/text()'
    )
    
   
    
  
    visited_urls = []


    def parse(self, response):
        link2="https://iz.ru"
        
        if response.url not in self.visited_urls:
            for link in response.xpath('//div[@class="lenta_news__day"]/div/a/@href').extract():
            
            
                url = urljoin(response.url, link)  
                yield scrapy.Request(url=url, callback=self.parse_document)
        next_pages = response.xpath('//a[contains(@class, "button")]/@href').extract()
        next_pages=next_pages[-1]
        
        more = urljoin(link2,next_pages)
        
        
        yield response.follow(more, callback=self.parse)
        
    def parse_document(self, response):
        for res in super().parse_document(response):
           
            yield res
            
            
            
            
            
            
            
            
            