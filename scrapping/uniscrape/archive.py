import tqdm

def process_archive(root):
    all_files = list(tqdm.tqdm(root.rglob('*.html.gz')))
    print("Processsing files in", root)
    for fpath in tqdm.tqdm(all_files):
        yield fpath
