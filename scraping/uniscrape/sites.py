import csv
import sys
from urllib.parse import urlparse

csv.field_size_limit(sys.maxsize)


def get_sites(sources):
    with open(sources, encoding='utf-8') as sources:
        reader = csv.reader(sources, delimiter='\t')
        data = list(reader)

    print(f"Found {len(data)} sites.")

    for row in data[1:]:
        if len(row) < 2:
            continue
        name = row[0]
        site = row[1]
        if '.' not in site:
            print(f"Skipping bad site: {site}")
            continue
        if '://' in site:
            yield name, site
        else:
            yield name, 'http://' + site
            yield name, 'https://' + site


def get_hostname(url):
    host = urlparse(url).hostname or ''
    return host


def get_sitename(url):
    host = get_hostname(url)
    if host.count('.') > 1:
        parts = host.split('.')
        if parts[-2] == 'co':  # e.g. www.site.co.uk
            host = '.'.join(parts[-3:])
        else:
            host = '.'.join(parts[-2:])
    return host


def is_same_site(url_a, url_b):
    return get_sitename(url_a) == get_sitename(url_b)
