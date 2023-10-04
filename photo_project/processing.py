from photo_project.model import *
from photo_project.measure import MeasureProgress,MeasureDuration
import pathlib
from datetime import timedelta,datetime
import logging
import cv2
import numpy as np

class Status:
    NEW         = 'new'
    ERROR       = 'error'
    TODO        = 'todo'
    PROCESSING  = 'processing'
    DONE        = 'done'

class PhotoProcessing:

    @property
    def name(self):
        return self.__class__.__name__

    def init_database(self):
        if self.name is not None and self.name != '':
            sql = """
            insert into photoprocess (photo_id,process_name,status,last_date)
            select t1.photo_id,?,?,datetime('now')
            from photo t1
            left join photoprocess t2 on (t2.photo_id == t1.photo_id and t2.process_name == ?)
            where t2.photo_id is null
            """
            database.execute_sql(sql,[self.name,Status.NEW,self.name])
            database.commit()
    
    def get(self,status_list:list[str]):
        query = ( PhotoProcess
            .select()
            .where(PhotoProcess.process_name == self.name and PhotoProcess.status << status_list)
        )
        return query
    
    def update_status(self,old_status,new_status):
        query =  ( PhotoProcess
            .update(status = new_status)
            .where(PhotoProcess.process_name == self.name and PhotoProcess.status == old_status)
        )
        query.execute()
    
    #abstracmethod
    def do_process(self,photo_process:PhotoProcess):
        pass

    def run(self):
        self.current_query = self.get([Status.TODO])
        photo_process:PhotoProcess
        for photo_process in self.current_query:
            photo_process.status = Status.PROCESSING
            photo_process.last_date = datetime.now()
            try:
                self.do_process(photo_process)
                photo_process.status = Status.DONE
                photo_process.save()
            except Exception as err:
                logging.error(f'Unable to process {self.name} on photo {photo_process.photo.full_path} {str(err)} ')
                photo_process.status = Status.ERROR
                photo_process.save()
        
class ExistsProcessing(PhotoProcessing):

    def do_process(self,photo_process:PhotoProcess):
        photo_process.photo.exists = pathlib.Path(photo_process.full_path).is_file()
        photo_process.photo.save()


class FaceDetect(PhotoProcessing):

    def __init__(self):
        self.default_model_file = "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(self.default_model_file)
        self.scale_factor = 1.3

    def set_image(self,image):
        self.current_image = image
        self.current_gray_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
    
    def find_overlap(self,rect,all_rect):
        if len(rect) == 4:
            x_1,y_1,w_1,h_1 = rect
            for (x,y,w,h) in all_rect:
                if  (x > x_1 and x < x_1+w) or (x+w_1 > x_1 and x+w_1 < x_1+w) and\
                    (y > y_1 and y < y_1+h) or (y+h_1 > y_1 and y+h_1 < y_1+h):
                    return True
        return False

    def get_faces_rectangles(self):
        all_faces = self.face_cascade.detectMultiScale(self.current_gray_image, self.scale_factor, 5)
        if len(all_faces) >  1:
            overlap = False
            for face in all_faces:
                overlap = self.find_overlap(face,all_faces)
                if overlap:
                    break
            if overlap:
                self.faces = [all_faces[0]]
            else:
                self.faces = all_faces
        else:
            self.faces = all_faces

        return self.faces

    def do_process(self,photo_process:PhotoProcess):
        #image = cv2.imread(photo_process,cv2.IMREAD_GRAYSCALE)
        image = cv2.imread(photo_process.photo.full_path)
        self.set_image(image)
        rects = self.get_faces_rectangles()
        for rect in rects:
            # todo check for overlap with existing in database
            PhotoPerson.create(photo=photo_process.photo,assigned_by=self.name)