from photo_project.model import *
from util_functions import find_overlap
from datetime import timedelta,datetime
import cv2
from util_functions import force_image_size

from enum import Enum
import logging

class Person2VideoMode(Enum):

    FULL = 1
    FACE = 2

class Person2Video:

    def __init__(self,person:Person):
        self.person = person
        self.face_output_size_w_h:tuple(int,int) = (600,600)
        #self.full_output_size_w_h:tuple(int,int) = (2560,1920)
        self.full_output_size_w_h:tuple(int,int) = (800,600)
        self.codec = 'H264'
        self.fps = 1
        self.inter=cv2.INTER_AREA
        self.full_images = []
        self.face_images = []

    def make(self,filename:str):
        self.load_images()
        self.write(filename)

    def load_images(self):
        self.full_images = []
        self.face_images = []

        query = ( PhotoPerson
            .select()
            .join(Photo,on=(PhotoPerson.photo == Photo.photo_id))
            .where( PhotoPerson.person_id == self.person.person_id)
            .order_by(Photo.timestamp.asc())
        )
        photo_person:PhotoPerson
        for photo_person in query:
            image_cv2 = cv2.imread(photo_person.photo.full_path)
            
            resized =cv2.resize(image_cv2, self.full_output_size_w_h, interpolation=self.inter)
            w,h = self.full_output_size_w_h
            #resized = force_image_size(image_cv2,width=w,height=h)
            logging.info(f"Resized for video from {image_cv2.shape} to {resized.shape} image: {photo_person.photo.full_path}")
            self.full_images.append(resized)
            
            face_img = image_cv2[photo_person.y:photo_person.y + photo_person.h, photo_person.x:photo_person.x + photo_person.w]
            w, h = self.face_output_size_w_h
            #face_img_resized = force_image_size(image_cv2,width=w,height=h)
            face_img_resized = cv2.resize(face_img, self.face_output_size_w_h, interpolation=self.inter)
            logging.info(f"Resized face for video from {face_img.shape} to {face_img_resized.shape} image: {photo_person.photo.full_path}")
            self.face_images.append(face_img_resized)
    
    
    def write(self,filename:str,mode:Person2VideoMode = Person2VideoMode.FACE):
        
        output_images:list()
        if mode == Person2VideoMode.FULL:
            output_images = self.full_images
            output_size = self.full_output_size_w_h
        elif mode == Person2VideoMode.FACE:
            output_images = self.face_images
            output_size = self.face_output_size_w_h
        else:
            raise ProgrammingError(f'Mode {mode} is not considered')
        
        out = cv2.VideoWriter(filename=filename,fourcc=cv2.VideoWriter_fourcc(*self.codec), fps=self.fps, frameSize=output_size)
        for image in output_images:
            out.write(image.astype('uint8'))
        out.release()
