import csv
import html
import io
import re
from urllib.parse import urljoin

import bleach
import bs4

from scrapping.uniscrape.store import is_same_site


def get_html_links(base_url, body):
    soup = bs4.BeautifulSoup(body, 'lxml')
    for element in soup.find_all('a', href=True):
        found_url = element.get('href', '')
        url = urljoin(base_url, found_url)
        if is_same_site(url, base_url):
            yield url


def html2text(text):
    text = bleach.clean(text, tags=['br', 'p', 'div', 'article', 'section', 'li', 'td', 'th', 'hr', 'dt'], strip=True)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'</?\w+[^>]*>', '\n', text)
    text = re.sub(r'\n\s+', '\n', text)
    text = re.sub(r'\s+\n', '\n', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def csv2string(rows):
    si = io.StringIO()
    cw = csv.writer(si)
    for row in rows:
        cw.writerow(row)
    return si.getvalue().strip('\r\n').encode('utf-8')
