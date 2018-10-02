import bs4
import re


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
    unique_hrefs = []

    # compile pattern for domain match
    pattern = re.compile(domain_name)
    # filter duplicates and links to other domains
    for href in hrefs:
        if href not in unique_hrefs:
            # append only urls from the same domain
            if re.match('.*' + domain_name + '.*', href):
                unique_hrefs.append(href)
            # append relative href, combine them with domain name
            if (href[0] == '/') and (href != '/'):
                unique_hrefs.append(domain_name + href)        
    # store values to txt file
    with open(output_file, 'w+') as file:
            for href in unique_hrefs:
                file.write(href + '\n')
    return(TRUE)