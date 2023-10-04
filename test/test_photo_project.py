from test.config import *
from test.make_data import *

from photo_project import *
import unittest
import time
from datetime import datetime


class TestModel(unittest.TestCase):

    def test_basic_db_functions(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        PhotoProject.set_current_database(db_file)
        
        Parameter.create(name='MODEL',value='test.yml')
        model = Parameter.select(Parameter.name == 'MODEL')
        self.assertIsNotNone(model)

        basedir = BaseDir.create(base_path = '~/tmp/test_fotos')
        self.assertIsNotNone(basedir)

        photo = Photo.create(base_dir=basedir , path='a_path',md5='asimpleMD5sum',timestamp = datetime(2010,2,7,11,45,59))
        self.assertIsNotNone(photo)
        
        self.assertEqual(photo.full_path,'~/tmp/test_fotos/a_path')

        photo.set_md5_from_file()

        PhotoProject.close_current_database()

    def test_load_directory(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        PhotoProject.set_current_database(db_file)

        base_path = make_test_files()

        basedir = BaseDir.create(base_path = base_path)
        self.assertIsNotNone(basedir)

        PhotoProject.basic_load_basedir(basedir)

        photo:Photo = Photo.select().where(Photo.base_dir == basedir and Photo.path == 'sub_dir_1/test_file_1.jpg').get()
        self.assertIsNotNone(photo)

        photo.set_timestamp_from_file()
        photo.set_md5_from_file()
        photo.save()

        PhotoProject.close_current_database()

    def do_processing(self,processing:PhotoProcessing):
        processing.init_database()
        test_list = [ process for process in  processing.get(status_list=[Status.NEW])]
        self.assertGreater(len(test_list),0)

        processing.run()
        test_list = [ process for process in  processing.get(status_list=[Status.NEW])]
        self.assertGreater(len(test_list),0)

        processing.update_status(old_status=Status.NEW,new_status=Status.TODO)
        test_list = [ process for process in  processing.get(status_list=[Status.NEW])]
        self.assertEqual(len(test_list),0)
        test_list = [ process for process in  processing.get(status_list=[Status.TODO])]
        self.assertGreater(len(test_list),0)

        processing.run()
        test_list = [ process for process in  processing.get(status_list=[Status.TODO])]
        self.assertEqual(len(test_list),0)
        test_list = [ process for process in  processing.get(status_list=[Status.DONE])]
        self.assertGreater(len(test_list),0)

    def test_processing(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        PhotoProject.set_current_database(db_file)
        base_path = make_test_files()

        basedir = BaseDir.create(base_path = base_path)
        self.assertIsNotNone(basedir)

        PhotoProject.basic_load_basedir(basedir)

        self.do_processing(PhotoProcessing() )
        self.do_processing(ExistsProcessing() )

        PhotoProject.close_current_database()