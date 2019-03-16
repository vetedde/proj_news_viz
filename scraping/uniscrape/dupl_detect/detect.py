import lmdb

from .utils import utils

db_path = ''


class TextsDB:
    def __init__(self, db_name):
        """
        takes path to lmdb which will uses for storing hashes
        """
        self.db_path = db_name
        self.env = lmdb.open(db_path)

    def add(self, file_path):
        """
        takes file path to new articles which will add to the base
        :returns dictionary with two elements
        intersection: intersection between new article and existing ones
        files: files which have the same pieces
        """
        paragraphs = utils.parse_article(file_path)
        chunks = utils.get_chunks(paragraphs)
        hash_dict = utils.get_hash_dict(file_path, chunks)

        duplicates = {}
        intersection_count = 0
        chunks_count = len(chunks) or 1
        with self.env.begin(write=True) as thx:
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

        max_intersection = intersection_count / chunks_count

        files_intersect = {k: v / chunks_count
                           for (k, v) in duplicates.items()}

        return {'max_intersection': max_intersection, 'files': files_intersect}
