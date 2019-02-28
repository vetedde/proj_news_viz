import gzip
import gzip
import os
import sys
from pathlib import Path

from readability.readability import Document

from scrapping.uniscrape.archive import process_archive
from scrapping.uniscrape.conf import ROOT, LISTS
from scrapping.uniscrape.globals import is_all_cool
from scrapping.uniscrape.htmls import csv2string, html2text, get_html_links
from scrapping.uniscrape.links import Links
from scrapping.uniscrape.store import FileStore, _load_page

all_links = Links(LISTS)


def parse_file(file_store: FileStore, src_path: Path):
    target_path = src_path.parent / src_path.name.replace('.html.gz', '.parsed.gz')
    if target_path.exists() and target_path.stat().st_size:
        return False
    fn = src_path.relative_to(file_store.root)
    # print("Rel path:", fn, "for", src_path)
    try:
        page = _load_page(file_store.load(str(fn)))
    except Exception:
        import traceback
        traceback.print_exc()
        return False

    if not is_all_cool(page.url):
        return False

    mtime = str(src_path.stat().st_mtime)

    if page.body.strip():
        try:
            doc = Document(page.body, url=page.url)

            # meta_path = src_path.parent / src_path.name.replace('.html.gz', '.meta.gz')

            links = get_html_links(page.url, page.body)
            for link in links:
                if is_all_cool(link):
                    all_links.add_link(link)
            info = {
                'status': 'OK',
                'url': page.url,
                'title': doc.short_title(),
                'text': html2text(doc.summary()),
                'downloaded': mtime,
            }
        except Exception:
            import traceback
            traceback.print_exc()
            info = {
                'status': 'ParseError',
                'url': page.url,
                'title': '',
                'text': '',
                'downloaded': mtime,
            }

    else:
        info = {
            'url': page.url,
            'status': 'NotForRobots',
            'title': '',
            'text': '',
            'downloaded': mtime,
        }
    # import pprint
    # pprint.pprint(info)

    ftmp = str(target_path) + '.tmp'
    with gzip.open(ftmp, 'wb') as f:
        f.write(csv2string(info.items()))
    os.rename(ftmp, target_path)

    return True


def main():
    global all_links
    root = Path(ROOT)
    file_store = FileStore(root)
    all_links = Links(LISTS)

    ok = 0
    search_root = root
    if len(sys.argv) > 1:
        search_root = root / sys.argv[1]
    for fpath in process_archive(search_root):
        if parse_file(file_store, fpath):
            ok += 1
    print("Successful parse:", ok)


if __name__ == '__main__':
    main()
