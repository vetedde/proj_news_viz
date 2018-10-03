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
    duplicates = {}
    intersection_count = 0
    chunks_count = len(chunks)
    with env.begin(write=True) as thx:
        for key, value in hash_dict.items():
            dt = thx.get(key.encode())
            if not dt:
                thx.put(key.encode(), value.encode())
                continue

            intersection_count += 1
            fname = dt.decode()
            if fname in duplicates:
                duplicates[fname] += 1
            else:
                duplicates[fname] = 1

    max_intersection = round(intersection_count / chunks_count, 2)

    files_intersect = {k: round(v / chunks_count, 2)
                       for (k, v) in duplicates.items()}

    return {'max_intersection': max_intersection, 'files': files_intersect}
