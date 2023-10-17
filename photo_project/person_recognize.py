from photo_project.model import *
from photo_project.measure import MeasureProgress,MeasureDuration
from util_functions import find_overlap
import pathlib
from datetime import timedelta,datetime
import logging
import cv2
import numpy as np
from util_functions import resize_image

class PersonRecognizer:

    def __init__(self,model_file:str):
        self.model_file = model_file
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.normalized_width = 200

        self.id_vs_name = dict()
        self.name_vs_id = dict()
        
        self.reload_model()

    def reload_model(self):
        if pathlib.Path(self.model_file).is_file():
            self.recognizer.read(self.model_file)
            #self._read_labels()

    def run_training_all(self):
        ids,faces = self. _read_all_train_data()
        if len(ids > 0):
            self.recognizer.train(faces,ids)
            self.recognizer.save(self.model_file)
        else:
            logging.warning('No training data set')

    """
    def _read_labels(self):
        self.id_vs_name = dict()
        self.name_vs_id = dict()
        for person in Person.select():
            self.id_vs_name[person.person_id] = person.name
            self.name_vs_id[person.name] = person.person_id
    """

    def _read_all_train_data(self):
        query = (
            PhotoPerson
            .select()
            .join(Photo,on=( Photo.photo_id == PhotoPerson.photo_id))
            .join(Person,on=( Person.person_id == PhotoPerson.person_id))
            .where(PhotoPerson.assigned_by == 'manual')
        )
        faces = []
        ids = []
        for photo_person in query:
            faceNP = self.get_person_normalized_image(photo_person)
            faces.append(faceNP)
            ids.append(photo_person.person.person_id)

        return np.array(ids), faces

    def get_person_normalized_image(self,photo_person:PhotoPerson,image_cv2_input = None):
        if image_cv2_input is None:
            image_cv2 = cv2.imread(photo_person.photo.full_path)
        else:
            image_cv2 = image_cv2_input
        
        face_img = resize_image(image_cv2[photo_person.y:photo_person.y + photo_person.h, photo_person.x:photo_person.x + photo_person.w], width = self.normalized_width)
        face_img_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        return np.array(face_img_gray, 'uint8')


    def predict(self,photo_person:PhotoPerson,image_cv2_input = None):
        faceNP = self.get_person_normalized_image(photo_person,image_cv2_input = image_cv2_input)
        id, confidence = self.recognizer.predict(faceNP)
        person = Person.get_by_id(id)
        return person, confidence

