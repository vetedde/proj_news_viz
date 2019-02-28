from urllib.parse import urljoin

import bs4

from scrapping.uniscrape.store import is_same_site


def get_html_links(base_url, body):
    soup = bs4.BeautifulSoup(body, 'lxml')
    for element in soup.find_all('a', href=True):
        found_url = element.get('href', '')
        url = urljoin(base_url, found_url)
        if is_same_site(url, base_url):
            yield url


