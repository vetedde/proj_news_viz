import bs4
import re
from urllib.parse import urlparse

def html_parser(html_path, domain_name, output_file):
    """ Html parser for self reference links
     html_parser parses html document for links belonging to
     the same domain and stores it to txt file with one URL per
     line.
    Args:
        html_path (str): Path to html file.
        domain_name (str): Domain name to search for.
        output_file (str): Path for output file
    """
    with open(html_path, encoding='utf8') as file:
        html = bs4.BeautifulSoup(file, "html.parser")
    # collect all a tags
    a_list = html.find_all('a', href=True)
    hrefs = [i['href'] for i in a_list]
    unique_urls = []
    # compile pattern for domain match
    pattern = re.compile(domain_name)
    # filter duplicates and links to other domains
    for href in hrefs:
        parsed_url = urlparse(href)
        # exlude mailto: schemes
        if parsed_url.scheme == 'mailto':
            continue
        # process urls
        # relative links --> absolute links
        if parsed_url.netloc == '':
            root_url = domain_name
        # domain check
        elif pattern.findall(parsed_url.netloc):
            root_url = parsed_url.netloc
        else:
            continue
        url = root_url + parsed_url.path
        # store only unique urls
        if url not in unique_urls:
            unique_urls.append(url)
    # store values to txt file
    with open(output_file, 'w+') as file:
            for url in unique_urls:
                file.write(url + '\n')
