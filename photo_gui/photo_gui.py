from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QErrorMessage,
    QAction,
    QFileDialog,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QSizePolicy
)

from PyQt5.QtCore import (
    QSettings
)  

from PyQt5.QtGui import (
    QKeySequence,
    QImage,
    QPixmap,
    
)

from photo_project import (
    PhotoProject,
    Photo
)

from util_functions import resize_image

import cv2
import random

class PhotosMainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__(None)
        self._init_file_menu()
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
        self.file_menu.addAction(self.open_action)

        self.close_action = QAction("&Close File")
        self.close_action.triggered.connect(self.close_file)
        self.file_menu.addAction(self.close_action)
        self.close_action.setEnabled(False)

        self.exit_action = QAction("&Exit")
        self.exit_action.triggered.connect(self.exit)
        self.file_menu.addAction(self.exit_action)

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
        self.right_layout = QVBoxLayout()
        self.im_layout = QVBoxLayout()
        self.navigation_layout = QHBoxLayout()

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


    def _init_help_menu(self):
        self.help_menu = self.menuBar().addMenu("&Help")
        self.about_action = QAction("&About")
        self.help_menu.addAction(self.about_action)

        self.about_action.triggered.connect(self.show_about_dialog)
    
    def open_file(self):
        path = QFileDialog.getOpenFileName(self, "Open",filter='*.db')[0]
        if path:
            PhotoProject.set_current_database(path)
            self.close_action.setEnabled(True)
            self.open_action.setEnabled(False)
            self.current_photos: list[Photo] = [ photo for photo in Photo.select().order_by(Photo.photo_id)]
            self.show_random_photo()
    
    def close_file(self):
        PhotoProject.close_current_database()
        self.close_action.setEnabled(False)
        self.open_action.setEnabled(True)

    def exit(self):
        if self.close_action.isEnabled():
            self.close_file()
        self.close()
    
    def show_next_photo(self):
        if len(self.current_photos) == 0:
            return
        self.set_current_photo_by_index(self.current_index + 1)
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
    settings = QSettings(app.organizationName(), app.applicationName())

    window = PhotosMainWindow()
    window.showMaximized()
    app.exec()

if __name__ == '__main__':
    start_app()