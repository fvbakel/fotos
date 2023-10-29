from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from photo_project import (
    PhotoProject,
    Photo,
    PhotoPerson,
    Person,
    PersonRecognizer,
    PersonRecognizerCombined,
    Person2Video,
    Person2VideoMode,
    PhotoQueryParameters
)

from util_functions import resize_image,force_image_size

import cv2
import random
import logging
from datetime import date

class PhotosMainWindow:
    pass

class QueryDialog(QDialog):

    def __init__(self, main_window:PhotosMainWindow ):
        super(QueryDialog, self).__init__(main_window)
        self.main_window = main_window
        self.query_parameters = PhotoQueryParameters()
        self.setWindowTitle('Custom query')
        
        self.layout = QGridLayout(self)

        self.person_list = QComboBox()
        self.person_list.addItem('')
        for person in Person.select():
                self.person_list.addItem(person.name)
        self.layout.addWidget(QLabel('Person'),1,0)
        self.layout.addWidget(self.person_list,1,2)

        self.assigned_by_list = QComboBox()
        # TODO: get values dynamic from from database
        self.assigned_by_list.addItems(['','manual','FaceDetect','PersonRecognize'])
        self.layout.addWidget(QLabel('Assigned_by'),2,0)
        self.layout.addWidget(self.assigned_by_list,2,2)

        self.path           = QLineEdit()
        self.path_operator  = QComboBox()
        self.path_operator.addItems(PhotoQueryParameters.STR_OPERATORS)
        self.layout.addWidget(QLabel('Path'),3,0)
        self.layout.addWidget(self.path_operator,3,1)
        self.layout.addWidget(self.path,3,2)

        self.nr_of_faces = QSpinBox(self) 
        self.nr_of_faces.setRange(0,20)
        self.nr_of_faces.setSpecialValueText('')
        self.nr_of_faces_operator  = QComboBox()
        self.nr_of_faces_operator.addItems(PhotoQueryParameters.NR_OPERATORS)
        self.layout.addWidget(QLabel('Nr of faces'),4,0)
        self.layout.addWidget(self.nr_of_faces_operator,4,1)
        self.layout.addWidget(self.nr_of_faces,4,2)

        self.nr_of_persons = QSpinBox(self) 
        self.nr_of_persons.setRange(0,20)
        self.nr_of_persons.setSpecialValueText('')
        self.nr_of_persons_operator  = QComboBox()
        self.nr_of_persons_operator.addItems(PhotoQueryParameters.NR_OPERATORS)
        self.layout.addWidget(QLabel('Nr of persons'),5,0)
        self.layout.addWidget(self.nr_of_persons_operator,5,1)
        self.layout.addWidget(self.nr_of_persons,5,2)

        self.exists_map = {
            '':                 None,
            'Exists':           True,
            'Does not exists':  False
        }
        self.is_existing = QComboBox()
        self.is_existing.addItems(self.exists_map.keys())
        self.layout.addWidget(QLabel('File status'),6,0)
        self.layout.addWidget(self.is_existing,6,2)

        self.duplicate_map = {
            '':                         None,
            'Has duplicates':           True,
            'Does not have duplicates': False
        }
        self.duplicate = QComboBox()
        self.duplicate.addItems(self.duplicate_map.keys())
        self.layout.addWidget(QLabel('Duplicates'),7,0)
        self.layout.addWidget(self.duplicate,7,2)

        self.min_date= QDate.fromString( "01/01/2000", "dd/MM/yyyy" )
        self.max_date = date.today()
        # TODO: get min and max value from database 
        self.after = QDateEdit(self)
        self.after.setCalendarPopup(True)
        self.after.setDate(self.min_date)
        self.after.setMinimumDate(self.min_date)
        self.after.setMaximumDate(self.max_date)
        self.layout.addWidget(QLabel('After'),10,0)
        self.layout.addWidget(self.after,10,2)

        self.before = QDateEdit(self)
        self.before.setCalendarPopup(True)
        self.before.setDate(self.max_date)
        self.before.setMinimumDate(self.min_date)
        self.before.setMaximumDate(self.max_date)
        self.layout.addWidget(QLabel('Before'),11,0)
        self.layout.addWidget(self.before,11,2)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def update_query_parameters(self):
        self.query_parameters.person_name   = self.person_list.currentText()
        self.query_parameters.assigned_by   = self.assigned_by_list.currentText()
        self.query_parameters.path          = self.path.text()
        self.query_parameters.path_operator = self.path_operator.currentText()

        self.query_parameters.nr_of_faces               = self.nr_of_faces.value()
        self.query_parameters.nr_of_faces_operator      = self.nr_of_faces_operator.currentText()
        self.query_parameters.nr_of_persons             = self.nr_of_persons.value()
        self.query_parameters.nr_of_persons_operator    = self.nr_of_persons_operator.currentText()

        self.query_parameters.after         = self.after.dateTime().toPyDateTime()
        self.query_parameters.before        = self.before.dateTime().toPyDateTime()

        self.query_parameters.is_existing   = self.exists_map[self.is_existing.currentText()]
        self.query_parameters.has_duplicate = self.duplicate_map[self.duplicate.currentText()]


    @staticmethod
    def get_query_parameters(main_window:PhotosMainWindow):
        dialog = QueryDialog(main_window)
        result = dialog.exec_()
        dialog.update_query_parameters()
        return (dialog.query_parameters, result == QDialog.Accepted)

class PhotosMainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__(None)
        self.person_image_width = 200
        self._init_file_menu()
        self._init_tools_menu()
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
    
    def _init_tools_menu(self):
        self.tools_menu = self.menuBar().addMenu("&Tools")
        self.train_action = QAction("&Run Training face model")
        self.train_action.triggered.connect(self.train_face_model)
        self.person_video_action = QAction("&Make person video")
        self.person_video_action.triggered.connect(self.make_person_video)

        self.tools_menu.addAction(self.train_action)
        self.tools_menu.addSeparator()
        self.tools_menu.addAction(self.person_video_action)

    def _init_query_menu(self):
        self.query_menu = self.menuBar().addMenu("&Query")

        self.query_group_act = QActionGroup(self.query_menu)
        texts = ["All", "Persons", "Recognized Persons","Custom","Duplicates"]
        functions = [self.query_all,self.query_persons,self.query_recognized,self.query_custom,self.query_duplicates]
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

        self.help_menu.addSeparator()
        self.logging_menu = self.help_menu.addMenu("&Logging")
        self.logging_group_act = QActionGroup(self.logging_menu)
        texts = ["CRITICAL", "ERROR", "WARN" ,"INFO","DEBUG"]
        levels = [logging.CRITICAL,logging.ERROR,logging.WARN,logging.INFO,logging.DEBUG]
        for text, level in zip(texts,levels):
            action = QAction(text, self.help_menu, checkable=True, checked=text==texts[0])
            self.logging_menu.addAction(action)
            action.level = level
            self.logging_group_act.addAction(action)
        self.logging_group_act.setExclusive(True)
        self.logging_group_act.triggered.connect(self.reset_logging)

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

        self.first_button = QPushButton('First')
        self.first_button.clicked.connect(self.show_first_photo)
        self.last_button = QPushButton('Last')
        self.last_button.clicked.connect(self.show_last_photo)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.main_wid = QWidget(self)
        self.setCentralWidget(self.main_wid)

        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QGridLayout()
        self.im_layout = QVBoxLayout()
        self.navigation_layout = QHBoxLayout()
        
        self.person_image_frame = QLabel()
        self.person_image_frame.setFixedWidth(self.person_image_width)
        self.person_image_frame.setFixedHeight(self.person_image_width)

        person_name_label = QLabel('Person name:') 
        person_assigned_by_label = QLabel('Assigned by:') 
        self.person_assigned_by = QLabel('') 

        self.photo_type = QComboBox()
        self.photo_type.addItems(['Normal','Gray','Normalized'])
        self.photo_type.currentTextChanged.connect(self.photo_type_changed)

        self.person_list = QComboBox()
        self.person_list.addItems(['Unknown','Not a person','New person'])
 
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

        self.prev_person_button = QPushButton('Previous')
        self.prev_person_button.clicked.connect(self.previous_person)
        self.next_person_button = QPushButton('Next')
        self.next_person_button.clicked.connect(self.next_person)

  
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_layout.addWidget(person_assigned_by_label,0,0)
        self.right_layout.addWidget(self.person_assigned_by,1,0)
        self.right_layout.addWidget(self.person_image_frame,2,0)
        self.right_layout.addWidget(self.photo_type,3,0)
        self.right_layout.addWidget(person_name_label,4,0)
        self.right_layout.addWidget(self.person_list,5,0)
        self.right_layout.addWidget(self.person_name,6,0 )
        self.right_layout.addWidget(self.save_button,7,0 )
        self.right_layout.addWidget(self.next_person_button,8,0 )
        self.right_layout.addWidget(self.prev_person_button,9,0 )
        
        self.right_layout.addWidget(person_predicted_label,20,0 )
        self.right_layout.addWidget(self.person_predicted,21,0 )

        self.right_layout.addWidget(person_confidence_label,22,0 )
        self.right_layout.addWidget(self.person_confidence,23,0 )

        self.navigation_layout.addWidget(self.first_button)
        self.navigation_layout.addWidget(self.prev_button)
        self.navigation_layout.addWidget(self.random_button)
        self.navigation_layout.addWidget(self.next_button)
        self.navigation_layout.addWidget(self.last_button)


        self.im_layout.addWidget(self.image_frame)
        
        self.left_layout.addWidget(self.info)
        self.left_layout.addLayout(self.navigation_layout)
        self.left_layout.addLayout(self.im_layout)
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)

        self.main_wid.setLayout(self.main_layout)

    def update_query(self, action:QAction):
        action.query()
        self.current_index = -1
        if len(self.current_photos) > 0:
            self.show_first_photo()
        else:
            self.clear_photo()

    def query_all(self):
        self.current_photos: list[Photo] = [ photo for photo in Photo.select().order_by(Photo.photo_id)]

    def query_persons(self):
        self.current_photos: list[Photo] = [ photo for photo in PhotoProject.get_persons()]

    def query_duplicates(self):
        self.current_photos: list[Photo] = [ photo for photo in PhotoProject.get_duplicates_as_objects()]
    
    def query_recognized(self):
        self.current_photos: list[Photo] = [ photo for photo in PhotoProject.get_recognized()]

    def query_custom(self):
        query_parameters, result = QueryDialog.get_query_parameters(self)
        if result:
            self.current_photos: list[Photo] = [ photo for photo in PhotoProject.get_custom(query_parameters)]
    
    def show_status_query(self):
        nrFound = len(self.current_photos)
        
        if nrFound > 0: 
            self.status_bar.showMessage(f'Found {nrFound} photos. Now showing photo {self.current_index + 1}')
        else:
            self.status_bar.showMessage(f'Found {nrFound} photos.')

    def train_face_model(self):
        self.recognizer.run_training_all()

    def make_person_video(self):
        person_name = self.person_list.currentText()
        if person_name == 'Unknown':
            return
        if person_name == 'Not a person':
            return
        if person_name == 'New person':
            person_name = self.person_name.text().strip()
            if len(person_name) == 0:
                return
            
        person = Person.get(name=person_name)
        person2video = Person2Video(person=person)
        person2video.load_images()

        filename = QFileDialog.getSaveFileName(self, "Save",filter='*.avi')[0]
        if filename:
            if not filename.endswith('.avi'):
                filename += '.avi'

            output_filename = filename.replace('.avi','_face.avi')    
            person2video.write(filename=output_filename,mode = Person2VideoMode.FACE)
            output_filename = filename.replace('.avi','_full.avi')
            person2video.write(filename=output_filename,mode=Person2VideoMode.FULL)

    def predict_person(self):
        if len(self.current_photo.persons) == 0 or not self.recognizer.is_trained:
            self.person_predicted.setText('')
            self.person_confidence.setText('')
            return
        photo_person:PhotoPerson = self.current_photo.persons[self.current_photo_person_index]
        
        person, confidence = self.recognizer.predict(photo_person)
        self.person_predicted.setText(person.name)
        self.person_confidence.setText(f'{confidence:0.3f} %')

    def save_person(self):
        if len(self.current_photo.persons) == 0:
            return
        
        photo_person:PhotoPerson = self.current_photo.persons[self.current_photo_person_index]
        person_name = self.person_list.currentText()
        if person_name == 'Unknown':
            pass
        if person_name == 'Not a person':
            pass
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
            
            self.recognizer = PersonRecognizer(recognizer_type='LBPH')
            #self.recognizer = PersonRecognizerCombined()
            self.query_all()
            self.show_random_photo()
            
    
    def close_file(self):
        PhotoProject.close_current_database()
        self.close_action.setEnabled(False)
        self.open_action.setEnabled(True)
        self.query_group_act.setEnabled(False)
        self.clear_photo()

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
    
    def show_last_photo(self):
        if len(self.current_photos) == 0:
            return
        self.set_current_photo_by_index(len(self.current_photos) -1)
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

    def clear_photo(self):
        self.image_frame.clear()
        self.info.setText('')
        self.show_status_query()
        self.clear_person()

    def show_photo(self):
        try:
            self.image_cv2 = cv2.imread(self.current_photo.full_path)
            for person in self.current_photo.persons:
                cv2.rectangle(self.image_cv2,(person.x,person.y),(person.x+person.w,person.y+person.h),(255,0,0),4)

            self.current_photo_person_index = 0
            self.display_person()

            frame_width = self.image_frame.size().width()
            frame_height = self.image_frame.size().height()
            #self.image_cv2_resized = resize_image(self.image_cv2,max_height=self.image_frame.size().height())
            self.image_cv2_resized = force_image_size(self.image_cv2,width=frame_width ,height=frame_height)
            
            logging.info(f"Resized for GUI from {self.image_cv2.shape} to {self.image_cv2_resized.shape} to fit frame w,h {frame_width},{frame_height}  image: {self.current_photo.full_path}")
            
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
            self.show_status_query()
        except Exception as err:
            logging.error(err)
            err_box = QMessageBox()
            err_box.setIcon(QMessageBox.Warning)
            err_box.setText('A error occurred in photo display')
            err_box.setDetailedText(str(err))
            err_box.setStandardButtons(QMessageBox.Ok)
            err_box.exec_()

    def next_person(self):
        if self.set_current_person_by_index(self.current_photo_person_index + 1):
            self.display_person()
    
    def previous_person(self):
        if self.set_current_person_by_index(self.current_photo_person_index - 1):
            self.display_person()

    def set_current_person_by_index(self,index:int):
        if index < 0 or index > (len(self.current_photo.persons) -1):
            return False
        self.current_photo_person_index = index
        return True

    def display_person(self):
        self.show_person_details()
        self.predict_person()

    def clear_person(self):
        self.person_image_frame.clear()
        name = 'Unknown'
        index = self.person_list.findText(name)
        self.person_list.setCurrentIndex(index)
        self.person_predicted.setText('')
        self.person_confidence.setText('')

    def show_person_details(self):
        self.person_name.setText('')
        if len(self.current_photo.persons) == 0:
            self.clear_person()
            return

        self.set_person_image()

        self.person_assigned_by.setText(self.current_photo.persons[self.current_photo_person_index].assigned_by)
        person:Person = self.current_photo.persons[self.current_photo_person_index].person
        if person is not None:
            name = person.name
        else:
            name = 'Unknown'
        index = self.person_list.findText(name)
        self.person_list.setCurrentIndex(index)

    def photo_type_changed(self,value):
        self.set_person_image()

    def set_person_image(self):
        if len(self.current_photo.persons) == 0:
            return None
        
        photo_person:PhotoPerson = self.current_photo.persons[self.current_photo_person_index]
        
        display_type = self.photo_type.currentText()
        if display_type == 'Normalized':
            person_img_cv2 = self.recognizer.get_person_normalized_image(photo_person=photo_person)
            self.person_image = QImage(
                person_img_cv2.data, 
                person_img_cv2.shape[1], 
                person_img_cv2.shape[0], 
                person_img_cv2.shape[1], 
                QImage.Format_Grayscale8
            )
        elif display_type == 'Gray':
            person_img_cv2 = resize_image(self.image_cv2[photo_person.y:photo_person.y + photo_person.h, photo_person.x:photo_person.x + photo_person.w],max_width=self.person_image_width)
            person_img_cv2 = cv2.cvtColor(person_img_cv2, cv2.COLOR_BGR2GRAY)
            self.person_image = QImage(
                person_img_cv2.data, 
                person_img_cv2.shape[1], 
                person_img_cv2.shape[0], 
                person_img_cv2.shape[1], 
                QImage.Format_Grayscale8
            )
        else:
            person_img_cv2 = resize_image(self.image_cv2[photo_person.y:photo_person.y + photo_person.h, photo_person.x:photo_person.x + photo_person.w],max_width=self.person_image_width)
            
            self.person_image = QImage(
                person_img_cv2.data, 
                person_img_cv2.shape[1], 
                person_img_cv2.shape[0], 
                person_img_cv2.strides[0], 
                QImage.Format_RGB888
            ).rgbSwapped()
        self.person_image_frame.setPixmap(QPixmap.fromImage(self.person_image))

    def show_about_dialog(self):
        text = "<center>" \
            "<h1>Foto's</h1>" \
            "&#8291;" \
            "<img src=icon.svg>" \
            "</center>" \
            "<p>Version 0.0.2<br/>" \
            "Copyright &copy; F. van Bakel.</p>"
        QMessageBox.about(self, "About my app", text)

    def reset_logging(self, action:QAction):

        level = action.level
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename='photo_gui.log',
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=level)
        logging.info('Logging reset')


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