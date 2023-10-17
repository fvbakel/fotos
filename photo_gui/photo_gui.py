from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from photo_project import (
    PhotoProject,
    Photo,
    PhotoPerson,
    Person,
    PersonRecognizer
)

from util_functions import resize_image

import cv2
import random

class PhotosMainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__(None)
        self._init_file_menu()
        self._init_edit_menu()
        self._init_query_menu()
        self._init_help_menu()
        self._init_photo_layout()
        self.current_photo:Photo = None
        self.current_photos: list[Photo] = []
        self.current_index:int = -1
        

    def _init_file_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")

        self.open_action = QAction("&Open")
        self.open_action.triggered.connect(self.open_file)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)

        self.close_action = QAction("&Close File")
        self.close_action.triggered.connect(self.close_file)       
        self.close_action.setEnabled(False)

        self.exit_action = QAction("&Exit")
        self.exit_action.triggered.connect(self.exit)

        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.close_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
    
    def _init_edit_menu(self):
        self.edit_menu = self.menuBar().addMenu("&Edit")
        self.train_action = QAction("&Run Training face model")
        self.train_action.triggered.connect(self.train_face_model)

        self.edit_menu.addAction(self.train_action)

    def _init_query_menu(self):
        self.query_menu = self.menuBar().addMenu("&Query")

        self.query_group_act = QActionGroup(self.query_menu)
        texts = ["All", "Persons", "Duplicates"]
        functions = [self.query_all,self.query_persons,self.query_duplicates]
        for text, function in zip(texts,functions):
            action = QAction(text, self.query_menu, checkable=True, checked=text==texts[0])
            self.query_menu.addAction(action)
            action.query = function
            self.query_group_act.addAction(action)
        self.query_group_act.setExclusive(True)
        self.query_group_act.triggered.connect(self.update_query)
        self.query_group_act.setEnabled(False)

    def _init_help_menu(self):
        self.help_menu = self.menuBar().addMenu("&Help")
        self.about_action = QAction("&About")
        self.help_menu.addAction(self.about_action)

        self.about_action.triggered.connect(self.show_about_dialog)

    def _init_photo_layout(self):
        self.image_frame = QLabel()
        self.info = QLabel()
        self.info.setMaximumHeight(15)
        self.prev_button = QPushButton('Previous')
        self.prev_button.clicked.connect(self.show_previous_photo)
        self.random_button = QPushButton('Random')
        self.random_button.clicked.connect(self.show_random_photo)
        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.show_next_photo)

        self.main_wid = QWidget(self)
        self.setCentralWidget(self.main_wid)

        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QGridLayout()
        self.im_layout = QVBoxLayout()
        self.navigation_layout = QHBoxLayout()
        
        self.person_image_frame = QLabel()
        self.person_image_frame.setFixedWidth(200)
        self.person_image_frame.setFixedHeight(200)

        person_name_label = QLabel('Person name:') 
        person_assigned_by_label = QLabel('Assigned by:') 
        self.person_assigned_by = QLabel('') 
        self.person_list = QComboBox()
        self.person_list.addItems(['Unkown','Not a person','New person'])
 
        self.person_name = QLineEdit()
        person_name_label.setFixedWidth(200)
        person_assigned_by_label.setFixedWidth(200)
        self.person_assigned_by.setFixedWidth(200)

        person_predicted_label = QLabel('Predicted person:') 
        self.person_predicted = QLabel('')
        
        person_confidence_label = QLabel('Confidence prediction:') 
        self.person_confidence = QLabel('')

        self.person_name.setFixedWidth(200)
        self.person_name.setMaxLength(255)
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_person)
  
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_layout.addWidget(person_assigned_by_label,0,0)
        self.right_layout.addWidget(self.person_assigned_by,1,0)
        self.right_layout.addWidget(self.person_image_frame,2,0)
        self.right_layout.addWidget(person_name_label,3,0)
        self.right_layout.addWidget(self.person_list,4,0)
        self.right_layout.addWidget(self.person_name,5,0 )
        self.right_layout.addWidget(self.save_button,6,0 )
        
        self.right_layout.addWidget(person_predicted_label,7,0 )
        self.right_layout.addWidget(self.person_predicted,8,0 )

        self.right_layout.addWidget(person_confidence_label,9,0 )
        self.right_layout.addWidget(self.person_confidence,10,0 )
               

        self.navigation_layout.addWidget(self.prev_button)
        self.navigation_layout.addWidget(self.random_button)
        self.navigation_layout.addWidget(self.next_button)
        self.im_layout.addWidget(self.image_frame)
        
        self.left_layout.addWidget(self.info)
        self.left_layout.addLayout(self.navigation_layout)
        self.left_layout.addLayout(self.im_layout)
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)

        self.main_wid.setLayout(self.main_layout)

    def update_query(self, action:QAction):
        action.query()
        self.show_first_photo()

    def query_all(self):
        self.current_photos: list[Photo] = [ photo for photo in Photo.select().order_by(Photo.photo_id)]
        self.current_index = -1

    def query_persons(self):
        self.current_photos: list[Photo] = [ photo for photo in PhotoProject.get_persons()]
        self.current_index = -1

    def query_duplicates(self):
        self.current_photos: list[Photo] = [ photo for photo in PhotoProject.get_duplicates_as_objects()]
        self.current_index = -1
    
    def train_face_model(self):
        self.recognizer.run_training_all()

    def predict_person(self):
        if len(self.current_photo.persons) == 0:
            self.person_predicted.setText('')
            self.person_confidence.setText('')
            return
        photo_person:PhotoPerson = self.current_photo.persons[0]
        
        person, confidence = self.recognizer.predict(photo_person)
        self.person_predicted.setText(person.name)
        self.person_confidence.setText(f'{100 - confidence:0.3f} %')

    def save_person(self):
        if len(self.current_photo.persons) == 0:
            return
        
        photo_person:PhotoPerson = self.current_photo.persons[0]
        person_name = self.person_list.currentText()
        if person_name == 'Unknown':
            return
        if person_name == 'Not a person':
            return
        if person_name == 'New person':
            person_name = self.person_name.text().strip()
            if len(person_name) == 0:
                return
        person, created = Person.get_or_create(name=person_name)
        if created:
            print(f'Created person: {person_name}')
            self.person_list.addItem(person_name)
        photo_person.person = person
        photo_person.assigned_by = 'manual'
        photo_person.save()

        self.person_assigned_by.setText(photo_person.assigned_by)

    def open_file(self):
        path = QFileDialog.getOpenFileName(self, "Open",filter='*.db')[0]
        if path:
            PhotoProject.set_current_database(path)
            self.close_action.setEnabled(True)
            self.open_action.setEnabled(False)
            self.query_group_act.setEnabled(True)

            for person in Person.select():
                self.person_list.addItem(person.name)
            
            self.recognizer = PersonRecognizer(model_file=PhotoProject.get_face_recognize_model())
            self.query_all()
            self.show_random_photo()
            
    
    def close_file(self):
        PhotoProject.close_current_database()
        self.close_action.setEnabled(False)
        self.open_action.setEnabled(True)
        self.query_group_act.setEnabled(False)

    def exit(self):
        if self.close_action.isEnabled():
            self.close_file()
        self.close()
    
    def show_next_photo(self):
        if len(self.current_photos) == 0:
            return
        self.set_current_photo_by_index(self.current_index + 1)
        self.show_photo()
    
    def show_first_photo(self):
        if len(self.current_photos) == 0:
            return
        self.set_current_photo_by_index(0)
        self.show_photo()

    def show_random_photo(self):
        if len(self.current_photos) == 0:
            return
        index = random.randint(0,len(self.current_photos))
        self.set_current_photo_by_index(index)
        self.show_photo()

    def show_previous_photo(self):
        if len(self.current_photos) == 0:
            return
        self.set_current_photo_by_index(self.current_index - 1)
        self.show_photo()

    def set_current_photo_by_index(self,index:int):
        if index < 0 or index > (len(self.current_photos) -1):
            return
        self.current_index = index
        self.current_photo = self.current_photos[self.current_index]

    def set_current_photo_by_id(self,photo_id:int = 1):
        self.current_photo:Photo = Photo.get_by_id(photo_id)
        self.current_index = -1

    def show_photo(self):
        try:
            self.image_cv2 = cv2.imread(self.current_photo.full_path)
            for person in self.current_photo.persons:
                cv2.rectangle(self.image_cv2,(person.x,person.y),(person.x+person.w,person.y+person.h),(255,0,0),4)

            self.show_person_image()
            self.predict_person()

            self.image_cv2_resized = resize_image(self.image_cv2,height=self.image_frame.size().height())
            
            self.image = QImage(
                self.image_cv2_resized.data, 
                self.image_cv2_resized.shape[1], 
                self.image_cv2_resized.shape[0], 
                self.image_cv2_resized.strides[0], 
                QImage.Format_RGB888
            ).rgbSwapped()
            self.image_frame.setPixmap(QPixmap.fromImage(self.image))
            #self.image_frame.setScaledContents( True )
            self.image_frame.setSizePolicy( QSizePolicy.Ignored, QSizePolicy.Ignored )
            self.info.setText(f"Photo: {self.current_photo.photo_id }: {self.current_photo.path}")
        except Exception as err:
            err_box = QErrorMessage()
            err_box.showMessage(str(err))
        

    def show_person_image(self):
        self.person_name.setText('')
        if len(self.current_photo.persons) == 0:
            self.person_image_frame.clear()
            return
        self.person_image_cv2 = self.get_person_image(200,200)
        self.person_image = QImage(
            self.person_image_cv2.data, 
            self.person_image_cv2.shape[1], 
            self.person_image_cv2.shape[0], 
            self.person_image_cv2.strides[0], 
            QImage.Format_RGB888
        ).rgbSwapped()
        self.person_image_frame.setPixmap(QPixmap.fromImage(self.person_image))

        self.person_assigned_by.setText(self.current_photo.persons[0].assigned_by)
        person:Person = self.current_photo.persons[0].person
        if person is not None:
            name = person.name
        else:
            name = 'Unkown'
        index = self.person_list.findText(name)
        self.person_list.setCurrentIndex(index)

    def get_person_image(self,out_w,out_h):
        if len(self.current_photo.persons) == 0:
            return None
        
        person:PhotoPerson = self.current_photo.persons[0]

        person_img = resize_image(self.image_cv2[person.y:person.y + person.h, person.x:person.x + person.w],width=200)

        return person_img

    def show_about_dialog(self):
        text = "<center>" \
            "<h1>Foto's</h1>" \
            "&#8291;" \
            "<img src=icon.svg>" \
            "</center>" \
            "<p>Version 0.0.2<br/>" \
            "Copyright &copy; F. van Bakel.</p>"
        QMessageBox.about(self, "About my app", text)


def start_app():

    app = QApplication([])
    app.setApplicationName("fotos")
    app.setOrganizationName("fvbakel")
    app.setApplicationDisplayName("Foto's");
    #settings = QSettings(app.organizationName(), app.applicationName())

    window = PhotosMainWindow()
    window.showMaximized()
    app.exec()

if __name__ == '__main__':
    start_app()