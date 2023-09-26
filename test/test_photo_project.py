from test.config import *
from photo_project import *
import logging
import unittest
import time

class TestModel(unittest.TestCase):

    def test_basic_db_functions(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        photoDB = PhotoProjectDB(db_file)
        photoDB.init_tables()
        
        model = photoDB.get_parameter('MODEL')
        self.assertIsNone(model)

        photoDB.add_parameter('MODEL','test.yml')
        model = photoDB.get_parameter('MODEL')
        self.assertIsNotNone(model)

        photoDB.add_basedir('~/tmp/test_fotos')
        basedir = photoDB.get_basedir(1)
        self.assertIsNotNone(basedir)

        photo = photoDB.get_photo('1')
        self.assertIsNone(photo)

        photoDB.add_photo([1,'a_path','asimpleMD5sum',1695713086])
        photofields = photoDB.get_photo('1')
        self.assertIsNotNone(photofields)

    def test_api(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        photoDB = PhotoProjectDB(db_file)
        photoDB.init_tables()

        project = PhotoProject(photoDB)

        base_path = '~/tmp/test_fotos'
        project.add_base_dir(base_path)
        base_dir = project.get_base_dir(1)
        self.assertIsNotNone(base_dir)
        base_dir = project.get_base_dir_on_path(base_path)
        self.assertIsNotNone(base_dir)

        photo = Photo(base_dir,'2007-10-28/PIC00001.jpg')
        project.add_photo(photo)
        self.assertGreater(photo.photo_id, 0)




