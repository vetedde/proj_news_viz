import hashlib
import os
import re

import bleach

TAGS = ['div', 'p', 'br', 'article', 'section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'dt', 'dd', 'td']


def parse_article(file_path):
    with open(file_path) as rf:
        html = rf.read()
    parts = re.split('<.*?>', html)
    parts = [re.sub(r'\W+', ' ', bleach.clean(p, strip=True, tags=TAGS)).strip() for p in parts]
    return filter(None, parts)


def get_chunks(paragraphs):
    chunks = []
    for i in range(1, len(paragraphs)):
        chunks.append(paragraphs[i - 1] + '\n' + paragraphs[i])
    if len(paragraphs) < 2:
        chunks.append('\n'.join(paragraphs))
    return chunks


def get_hash_dict(file_path, chunks):
    hash_dict = {}
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    for chunk in chunks:
        chunk_hash = hashlib.sha1(chunk.encode('UTF-8')).hexdigest()
        hash_dict[chunk_hash] = file_name
    return hash_dict
