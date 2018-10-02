import lmdb
from .utils import utils

db_path = ''


def init(db_name):
    '''
    takes path to lmdb which will uses for storing hashes
    '''
    global db_path
    db_path = db_name


def put(file_path):
    '''
    takes file path to new articles which will add to the base
    return dictionary with two elements
    intersection: score of intersection new article with existing ones
    files: files which have the same pieces
    '''
    paragraphs = utils.read_article(file_path)
    chunks = utils.get_chunks(paragraphs)
    hash_dict = utils.get_hash_dict(file_path, chunks)

    env = lmdb.open(db_path)
    duplicates = []
    with env.begin(write=True) as thx:
        for key, value in hash_dict.items():
            dt = thx.get(key.encode())
            if dt:
                duplicates.append(dt.decode())
            else:
                thx.put(key.encode(), value.encode())

    intersection = round(len(duplicates) / len(chunks), 2)
    return {'intersection': intersection, 'files': duplicates}
