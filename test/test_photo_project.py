from test.config import *
from test.make_data import *

from photo_project import *
import logging
import unittest
import time
from datetime import datetime
import file_utils


class TestModel(unittest.TestCase):

    def test_basic_db_functions(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        set_current_database(db_file)
        create_tables()
        
        Parameter.create(name='MODEL',value='test.yml')
        model = Parameter.select(Parameter.name == 'MODEL')
        self.assertIsNotNone(model)

        basedir = BaseDir.create(base_path = '~/tmp/test_fotos')
        self.assertIsNotNone(basedir)

        photo = Photo.create(base_dir=basedir , path='a_path',md5='asimpleMD5sum',timestamp = datetime(2010,2,7,11,45,59))
        self.assertIsNotNone(photo)
        
        self.assertEqual(photo.full_path,'~/tmp/test_fotos/a_path')

        photo.set_md5_from_file()

        close_current_database()

    def test_load_directory(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        set_current_database(db_file)
        create_tables()

        project = PhotoProject()
        base_path = make_test_files()

        basedir = BaseDir.create(base_path = base_path)
        self.assertIsNotNone(basedir)

        project.basic_load_basedir(basedir)

        photo:Photo = Photo.select().where(Photo.base_dir == basedir and Photo.path == 'sub_dir_1/test_file_1.jpg').get()
        self.assertIsNotNone(photo)

        photo.set_timestamp_from_file()
        photo.set_md5_from_file()
        photo.save()

        close_current_database()
