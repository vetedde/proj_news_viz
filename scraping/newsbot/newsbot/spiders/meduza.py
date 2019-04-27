import json
from urllib.parse import urlsplit
from datetime import datetime

import scrapy
from newsbot.items import Document
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.loader import ItemLoader


class MeduzaSpider(NewsSpider):
    name = 'meduza'

    # Page link template
    page_link_tmpl = 'https://meduza.io/api/v3/search?chrono=news&page={}&per_page=24&locale=ru'
    # Article link template
    article_link_tmpl = 'https://meduza.io/api/w4/{}'
    # Start with the first page
    start_urls = [page_link_tmpl.format(0)]

    config = NewsSpiderConfig(
        title_path='_',
        date_path='_',
        date_format='%Y-%m-%d %H:%M:%S',
        text_path='_',
        topics_path='_',
        authors_path='_'
    )

    def parse(self, response):
        last_page = False

        jsonresponse = json.loads(response.body_as_unicode())

        # Getting article items
        articles = [content for _, content in jsonresponse['documents'].items()]
        # Sorting them from the most recent to the most late one
        articles = sorted(articles, key=lambda x: x['published_at'], reverse=True)

        # Filtering out late articles and checking if we have reached the "until_date"
        filtered_articles = []
        for content in articles:
            pub_date = datetime.strptime(content['pub_date'], '%Y-%m-%d').date()
            if pub_date >= self.until_date:
                filtered_articles.append(content)
            else:
                last_page = True

        # Iterating through news on this page
        for content in filtered_articles:
            full_url = self.article_link_tmpl.format(content['url'])

            yield scrapy.Request(url=full_url, callback=self.parse_document)

        # Requesting a new page if needed
        if not last_page and jsonresponse['has_next']:
            page_depth = response.meta.get('page_depth', 1)

            link_url = self.page_link_tmpl.format(page_depth)

            yield scrapy.Request(url=link_url,
                                 priority=100,
                                 callback=self.parse,
                                 meta={'page_depth': page_depth + 1}
                                 )

    def parse_document(self, response):
        news_item = json.loads(response.body_as_unicode())['root']
        url = 'https://meduza.io/{}'.format(news_item['url'])

        # Taking all blocks from response with information
        blocks = self._get_text_blocks(news_item)

        # Extract text paragraphs from every block of the article
        text_paragraphs = self._extract_text_from_blocks(blocks)

        base_edition = urlsplit(self.start_urls[0])[1]
        edition = urlsplit(url)[1]

        # Replace every \xa0 with space
        text_paragraphs = [text.replace('\xa0', ' ') for text in text_paragraphs]
        title = news_item['title'].replace('\xa0', ' ')

        # Constructing the resulting item
        l = ItemLoader(item=Document(), response=response)
        l.add_value('url', url)
        l.add_value('edition', '-' if edition == base_edition else edition)
        l.add_value('title', title)
        l.add_value('topics', '')
        l.add_value('date', datetime.utcfromtimestamp(news_item['datetime']).strftime(self.config.date_format))
        l.add_value('text', text_paragraphs if text_paragraphs else [''])
        l.add_value('authors', news_item['source']['name'] if 'source' in news_item else [''])

        yield l.load_item()

    def _extract_text_from_blocks(self, blocks):
        text_paragraphs = []

        # Block types which contain text
        block_types = ['p', 'context_p', 'blockquote',
                       'image', 'h3', 'card_title', 'ul', 'lead']
        for block in blocks:
            if block['type'] in block_types:
                if block['type'] == 'image':
                    text_paragraphs.append(block['data'].get('caption', ''))
                elif block['type'] == 'card_title':
                    text_paragraphs.append(block['data'].get('text', ''))
                elif block['type'] == 'ul':
                    for one_elem in block['data']:
                        text_paragraphs.append(one_elem)
                else:
                    # Paragraphs can be empty (without text)
                    text_paragraphs.append(block.get('data', ''))

        return text_paragraphs

    def _get_text_blocks(self, news_item):
        blocks = []

        # Get all blocks with data depending on article type (news, slides, cards)
        if 'blocks' in news_item['content']:
            blocks = news_item['content']['blocks']
        elif 'slides' in news_item['content']:
            # Joining all slides into a list of blocks
            for one_slide in news_item['content']['slides']:
                for block in one_slide['blocks']:
                    blocks.append(block)
        elif 'cards' in news_item['content']:
            # Joining all cards into a list of blocks
            for one_slide in news_item['content']['cards']:
                for block in one_slide['blocks']:
                    blocks.append(block)

        return blocks
