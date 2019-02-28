import csv


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
