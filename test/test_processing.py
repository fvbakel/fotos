from test.config import *

from photo_project import *
import unittest



class TestFaceDetect(unittest.TestCase):

    def test_face_detect(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        PhotoProject.set_current_database(db_file)

        basedir = BaseDir.create(base_path = TEST_PHOTO_BASE_DIR)
        self.assertIsNotNone(basedir)

        PhotoProject.basic_load_basedir(basedir)

        processing = FaceDetect()
        processing.init_database()
        processing.update_status(Status.NEW,Status.TODO)
        processing.run()

        PhotoProject.close_current_database()

