from test.config import *
from test.make_data import *
from util_functions import *
import logging
import unittest


class TestUtils(unittest.TestCase):

    def test_get_files(self):
        test_files_dir_str = make_test_files()
        files = list(get_files(test_files_dir_str,('jpg','jpeg')))

        self.assertEqual(len(files),8)
        logging.info(f'Files: {files}')


    def test_overlap_line(self):
        line_1 = (11,15)
        line_2 = (1,2)
        self.assertFalse(find_overlap_line(line_1,line_2))

        # start before case
        line_2 = (1,11)
        self.assertFalse(find_overlap_line(line_1,line_2))
        
        line_2 = (1,12)
        self.assertTrue(find_overlap_line(line_1,line_2))

        line_2 = (12,13)
        self.assertTrue(find_overlap_line(line_1,line_2))

        line_2 = (12,15)
        self.assertTrue(find_overlap_line(line_1,line_2))

        line_2 = (1,16)
        self.assertTrue(find_overlap_line(line_1,line_2))

        line_2 = (12,20)
        self.assertTrue(find_overlap_line(line_1,line_2))

        # start inside
        line_2 = (11,12)
        self.assertTrue(find_overlap_line(line_1,line_2))

        line_2 = (12,13)
        self.assertTrue(find_overlap_line(line_1,line_2))

        line_2 = (12,15)
        self.assertTrue(find_overlap_line(line_1,line_2))

        line_2 = (12,16)
        self.assertTrue(find_overlap_line(line_1,line_2))

        line_2 = (12,20)
        self.assertTrue(find_overlap_line(line_1,line_2))

        # start outside
        line_2 = (15,16)
        self.assertFalse(find_overlap_line(line_1,line_2))

        line_2 = (15,20)
        self.assertFalse(find_overlap_line(line_1,line_2))


    def test_overlap(self):
        rect = (11,11,3,3)
        all_rect = ()
        self.assertFalse(find_overlap(rect,all_rect))

        all_rect = ((3,3,2,2),)
        self.assertFalse(find_overlap(rect,all_rect))

        all_rect = ((3,3,2,12),)
        self.assertFalse(find_overlap(rect,all_rect))

        all_rect = ((3,3,12,2),)
        self.assertFalse(find_overlap(rect,all_rect))

        # left top corner overlap
        all_rect = ((9,9,3,3),)
        self.assertTrue(find_overlap(rect,all_rect))

        # right bottom corner overlap
        all_rect = ((13,13,2,2),)
        self.assertTrue(find_overlap(rect,all_rect))

        # rect full encloses existing
        all_rect = ((12,12,1,1),)
        self.assertTrue(find_overlap(rect,all_rect))

        # rect is fully inside existing
        all_rect = ((10,10,5,5),)
        self.assertTrue(find_overlap(rect,all_rect))


