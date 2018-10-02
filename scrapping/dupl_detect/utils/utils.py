import bleach
import re
import hashlib
import os


def read_article(file_path):
    with open(file_path) as rf:
        html = rf.read()
    return [re.sub('\W+', '', bleach.clean(p, strip=True))
            for p in re.split('</p>|<br>|</br>', html)
            if bleach.clean(p, strip=True).strip()]


def get_chunks(paragraphs):
    chunks = []
    for i in range(1, len(paragraphs), 2):
        chunks.append(paragraphs[i-1] + paragraphs[i])
    if len(paragraphs) % 2:
        chunks.append(paragraphs[-1])
    if len(paragraphs) > 2:
        chunks.append(''.join(paragraphs))
    return chunks


def get_hash_dict(file_path, chunks):
    hash_dict = {}
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    for chunk in chunks:
        chunk_hash = hashlib.sha1(chunk.encode('UTF-8')).hexdigest()
        hash_dict[chunk_hash] = file_name
    return hash_dict
