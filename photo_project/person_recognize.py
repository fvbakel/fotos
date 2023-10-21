from photo_project.model import *
from photo_project.photo_project import PhotoProject
from photo_project.measure import MeasureProgress,MeasureDuration
from util_functions import find_overlap
import pathlib
from datetime import timedelta,datetime
import logging
import cv2
import numpy as np
from util_functions import resize_image

class PersonRecognizer:

    def __init__(self,recognizer_type:str='LBPH'):
        self._model_file = PhotoProject.get_face_recognize_model(recognizer_type=recognizer_type)
        self._recognizer_type = recognizer_type
        self._max_distance = 100
        if recognizer_type == 'LBPH':
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        elif recognizer_type == 'Eigen':
            self.recognizer = cv2.face.EigenFaceRecognizer_create()
            self._max_distance = 2000
        elif recognizer_type == 'Fisher':
            self.recognizer = cv2.face.FisherFaceRecognizer_create()
            self._max_distance = 2000
        else:
            raise ValueError(f'Unexpected recognizer_type: {recognizer_type}' )
        self.normalized_width = 200
        self.is_loaded = False
        self.reload_model()

    def reload_model(self):
        if pathlib.Path(self._model_file).is_file():
            self.recognizer.read(self._model_file)
            self.is_loaded = True

    def run_training_all(self):
        ids,faces = self._read_all_train_data()
        if len(ids > 0):
            self.recognizer.train(faces,ids)
            self.recognizer.save(self._model_file)
            self.is_loaded = True
        else:
            logging.warning('No training data set')

    def _read_all_train_data(self):
        query = (
            PhotoPerson
            .select()
            .join(Photo,on=( Photo.photo_id == PhotoPerson.photo_id))
            .join(Person,on=( Person.person_id == PhotoPerson.person_id))
            .where((PhotoPerson.assigned_by == 'manual') & (Person.name.not_in(['Unknown','Not a person'])))
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
        
        face_img = image_cv2[photo_person.y:photo_person.y + photo_person.h, photo_person.x:photo_person.x + photo_person.w]
        face_img_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        face_img_resized = resize_image(face_img_gray, max_width = self.normalized_width,max_height=self.normalized_width)
        #face_img_equalized = cv2.equalizeHist(face_img_resized)
        #mask = np.zeros((self.normalized_width, self.normalized_width))
        #face_img_normalized = cv2.normalize(face_img_equalized, mask, 0, 255, cv2.NORM_MINMAX)

        return np.array(face_img_resized, 'uint8')
    
    def get_person_normalized_image_as_cv2(self,photo_person:PhotoPerson,image_cv2_input = None):
        if image_cv2_input is None:
            image_cv2 = cv2.imread(photo_person.photo.full_path)
        else:
            image_cv2 = image_cv2_input
        
        face_img = image_cv2[photo_person.y:photo_person.y + photo_person.h, photo_person.x:photo_person.x + photo_person.w]
        
        face_img_resized = resize_image(face_img, max_width = self.normalized_width,max_height=self.normalized_width)
        face_img_gray = cv2.cvtColor(face_img_resized, cv2.COLOR_BGR2GRAY)
        #face_img_equalized = cv2.equalizeHist(face_img_resized)
        #mask = np.zeros((self.normalized_width, self.normalized_width))
        #face_img_normalized = cv2.normalize(face_img_equalized, mask, 0, 255, cv2.NORM_MINMAX)

        return face_img_gray


    def predict(self,photo_person:PhotoPerson,image_cv2_input = None):
        faceNP = self.get_person_normalized_image(photo_person,image_cv2_input = image_cv2_input)
        id, distance = self.recognizer.predict(faceNP)
        if distance > self._max_distance:
            distance = self._max_distance

        confidence = ((self._max_distance - distance)/self._max_distance) * 100
        person = Person.get_by_id(id)
        return person, confidence

class PersonRecognizerCombined:

    def __init__(self,recognizer_types:list[str]=['LBPH','Eigen','Fisher']):
        if len(recognizer_types) == 0:
            raise ValueError(f'Need at least one recognizer type')
        self._recognizer_types = recognizer_types
        self.recognizers:list[PersonRecognizer] = []

        for recognizer_type in self._recognizer_types:
            self.recognizers.append(PersonRecognizer(recognizer_type=recognizer_type))
        
    def run_training_all(self):
        for recognizer in self.recognizers:
            recognizer.run_training_all()

    def is_trained(self):
        for recognizer in self.recognizers:
            if not recognizer.is_loaded:
                return False
        return True

    def predict(self,photo_person:PhotoPerson,image_cv2_input = None):
        predictions = dict()
        for recognizer in self.recognizers:
            person, confidence = recognizer.predict(photo_person,image_cv2_input)
            if person not in predictions:
                predictions[person] = []
            predictions[person].append(confidence)

        if len(predictions) == 0:
            raise ProgrammingError('Should get some predictions')
        
        max_person:Person = None
        max_agree = 0
        max_confidence = 0
        for person,confidences in predictions.items():
            if len(confidences) > max_agree:
                max_agree = len(confidences)
                max_person = person
            if max_agree == 1 and max(confidences) < max_confidence:
                max_person = person
                max_confidence = max(confidences)
                

        if max_agree == len(self.recognizers):
            confidence = 100
        elif max_agree > 1:
            confidence = max(predictions[max_person])
        else:
            confidence = 0

        return max_person, confidence