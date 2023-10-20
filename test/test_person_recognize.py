from test.config import *

from photo_project import *
import unittest



class TestPersonRecognize(unittest.TestCase):

    def test_person_recognize(self):
        time_stamp = time.time()
        db_file = f"{TEST_TMP_DIR}/{time_stamp}.db"
        PhotoProject.set_current_database(db_file)

        basedir = BaseDir.create(base_path = TEST_PHOTO_BASE_DIR)
        self.assertIsNotNone(basedir)

        PhotoProject.reload_basedir(basedir)

        processing = FaceDetect()
        processing.init_database()
        processing.update_status(Status.NEW,Status.TODO)
        processing.run()

        
        recognizer = PersonRecognizer()

        # training with no persons should not fail
        recognizer.run_training_all()

        person_1 = Person.create(name='Person_1')
        person_2 = Person.create(name='Person_2')
        for index,photo_person in enumerate(PhotoPerson.select()):
            if index < 2:
                photo_person.assigned_by = 'manual'
            if index == 0:
                photo_person.person = person_1
            if index == 1:
                photo_person.person = person_2
            photo_person.save()

        recognizer.run_training_all()

        for index,photo_person in enumerate(PhotoPerson.select()):
            person, confidence = recognizer.predict(photo_person)
            if index == 0:
                self.assertEqual(person.name,person_1.name)
            if index == 1:
                self.assertEqual(person.name,person_2.name)



        PhotoProject.close_current_database()

