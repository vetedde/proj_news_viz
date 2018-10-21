from urllib.parse import urljoin, urlsplit

import bs4


def get_html_links(base_url, body):
    base_parsed = urlsplit(base_url, scheme='http')
    base_domain = base_parsed.netloc
    if base_domain.count('.') > 1:
        parts = base_domain.split('.')
        if parts[-2] == 'co':  # e.g. www.site.co.uk
            base_domain = '.'.join(parts[-3:])
        else:
            base_domain = '.'.join(parts[-2:])
    soup = bs4.BeautifulSoup(body, 'lxml')

    for element in soup.find_all('a', href=True):
        url = element.get('href', '')

        parsed_url = urlsplit(url, scheme=base_parsed.scheme)
        if parsed_url.scheme not in ['', 'http', 'https']:
            continue
        if parsed_url.netloc:  # this is an absolute link
            domain = '.' + parsed_url.netloc
            if not domain.endswith('.' + base_domain):
                continue

        yield urljoin(base_url, url)


def process_html_file(base_url: str, html_path: str, save_path: str):
    """
    Html parser for self reference links
    html_parser parses html document for links belonging to
    the same domain and stores it to txt file with one URL per
    line.
    Arguments:
        html_path (str): Path to html file.
        base_url (str): Domain name to search for.
        save_path (str): Path for output file
    """
    with open(html_path, encoding='utf8') as file:
        html = file.read()

    unique_urls = []
    for url in get_html_links(base_url, html):
        if url not in unique_urls:
            unique_urls.append(url)

    with open(save_path, 'w+') as file:
        for url in unique_urls:
            file.write(url + '\n')


if __name__ == '__main__':
    process_html_file('https://lenta.ru', '')
