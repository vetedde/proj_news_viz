import os
import shutil
from .. import detect
import unittest

db_path = os.path.abspath('testdb42')
file1_path = os.path.join(os.path.dirname(__file__) + '/test_dt/a1.html')
file2_path = os.path.join(os.path.dirname(__file__) + '/test_dt/a2.html')
file12_path = os.path.join(os.path.dirname(__file__) + '/test_dt/a12.html')


class TestPut(unittest.TestCase):

    def setUp(self):
        if os.path.exists(db_path):
            shutil.rmtree(db_path)

        detect.init(db_path)

    def tearDown(self):
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
            pass

    def test_completely_new(self):
        file_path = os.path.abspath(file2_path)
        result = detect.put(file_path)
        self.assertEqual(result['intersection'], 0)
        self.assertEqual(len(result['files']), 0)

        file_path = os.path.abspath(file1_path)
        result = detect.put(file_path)
        self.assertEqual(result['intersection'], 0)
        self.assertEqual(len(result['files']), 0)

    def test_completely_same(self):
        file_path = os.path.abspath(file2_path)
        detect.put(file_path)
        result = detect.put(file_path)
        self.assertEqual(result['intersection'], 1)
        self.assertEqual(len(result['files']), 6)

    def test_intersection(self):
        file_path = os.path.abspath(file12_path)
        detect.put(file_path)

        file_path = os.path.abspath(file1_path)
        result = detect.put(file_path)
        self.assertEqual(result['intersection'], 0.75)
        self.assertEqual(len(result['files']), 3)

        file_path = os.path.abspath(file2_path)
        result = detect.put(file_path)
        self.assertEqual(result['intersection'], 0.83)
        self.assertEqual(len(result['files']), 5)


if __name__ == '__main__':
    unittest.main()
