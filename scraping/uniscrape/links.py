from scrapping.uniscrape.store import build_dpid

links_added = set()

links_file = None

MAX_LINKS = 20000


def save_links(folder, urls):
    dt, tm = build_dpid().split('-', 1)
    fn = f'{dt}/feeds-{tm}.txt'
    path = folder / fn
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(folder / fn, 'w') as f:
        f.write('\n'.join(sorted(urls)))
    return path


class Links:
    def __init__(self, folder):
        self.folder = folder
        self.links = set()

    def add_link(self, link):
        if link in links_added:
            return False

        links_added.add(link)
        self.links.add(link)
        if len(self.links) > MAX_LINKS:
            self.save_links()
        return True

    def save_links(self):
        save_links(self.folder, self.links)
        self.links = set()

    def close(self):
        if self.links:
            self.save_links()

    def __del__(self):
        self.close()


def load_links(fpath: str):
    with open(fpath, 'r') as fin:
        urls = [line.strip() for line in fin]
    return urls


class LinksFolder:
    def __init__(self, folder):
        self.loaded = set()
        self.folder = folder

    def load_files(self):
        for path_fn in sorted(self.folder.rglob('*.txt'), reverse=True):
            fn = str(path_fn)
            if fn in self.loaded:
                continue
            self.loaded.add(fn)
            yield path_fn, load_links(fn)
