from test.config import *
from test.make_data import *
from file_utils import *
import logging
import unittest
import time
import pathlib
import shutil


class TestFileUtils(unittest.TestCase):

    def test_get_files(self):
        test_files_dir_str = make_test_files()
        files = list(get_files(test_files_dir_str,('jpg','jpeg')))

        self.assertEqual(len(files),8)
        logging.info(f'Files: {files}')


