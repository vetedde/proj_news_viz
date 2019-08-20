#!/usr/bin/python3

import requests
from time import sleep
from bs4 import BeautifulSoup as bs
from typing import List, Tuple


def _concat_url(url: str, postfixes: Tuple[str]):
    '''Make a list of urls to scrapy.
    '''
    return [url + postfix for postfix in postfixes]


def _responsible_scraping(url, pause):
    '''Make a sleep in between the requests.
    '''
    sleep(pause)
    return requests.get(url)


def _get_responses(urls: List[str]) -> List:
    '''Make a list of responses.
    '''
    return [_responsible_scraping(url, 1) for url in urls]


def _into_text(responses: List) -> List:
    ''''''
    return [response.text for response in responses]


def _make_soups(htmls):
    return [bs(html, 'html.parser') for html in htmls]


def _filter_by_predicates(string):
    '''Check if any of predicates are True.
    '''
    predicates = [
        lambda string: 'newpage' in str(string),
        lambda string: 'font-size' in str(string),
    ]

    return any([predicate(string) for predicate in predicates])


def process_data(url, postfixes):
    '''Process web using inner functions.
    Return soups.
    '''
    _urls = _concat_url(URL, postfixes)

    _responses = _get_responses(_urls)

    _htmls = _into_text(_responses)

    return _make_soups(_htmls)


def get_entities(soups):
    '''Get geo entities from soups.
    '''
    entities = ['']

    for batch in soups:
        for string in batch.find_all('li'):
            if _filter_by_predicates(string):

                # Replace separator after first word.
                string = string.text.replace(',', '|', 1)

                entities.append(string)

    return entities


def write_to_file(filename, lines):
    '''Write data to a file.
    '''
    with open(filename, 'a') as f:
        # Write header.
        f.writelines('city|description\n')
        # Write data, passing 2 first strings.
        [f.writelines(line + '\n') for line in lines[2:]]

    return 0


if __name__ == '__main__':

    # Alphabetical indices for geo objects,
    # as it organized at http://geoportalwiki.wikidot.com/start.
    POSTFIXES = ('a', 'b', 'v', 'g', 'd', 'yo', 'zh', 'z', 'i', 'j',
                 'k1', 'k2', 'l', 'm', 'n', 'o', 'p', 'r', 's1', 's2',
                 't', 'u', 'f', 'kh', 'tc', 'ch', 'sh', 'shch', 'y',
                 'e', 'iu', 'ia')

    # Base url to concatenate with postfixes.
    URL = \
        'http://geoportalwiki.wikidot.com/'\
        'slovar-geograficheskikh-nazvanii-zarubezhny-kh-stran-'

    # Where to write a data.
    FILENAME = 'geo_entities_world_geowiki.csv'

    soups = process_data(URL, POSTFIXES)
    entities = get_entities(soups)

    write_to_file(FILENAME, entities)
