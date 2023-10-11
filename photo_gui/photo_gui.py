from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QAction,
    QFileDialog
)

from PyQt5.QtCore import (
    QSettings    
)  

from PyQt5.QtGui import QKeySequence

from photo_project import PhotoProject


class PhotosMainWindow(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__(None)
        self._init_file_menu()
        self._init_help_menu()
        

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
            
    
    def close_file(self):
        PhotoProject.close_current_database()
        self.close_action.setEnabled(False)
        self.open_action.setEnabled(True)

    def exit(self):
        if self.close_action.isEnabled():
            self.close_file()
        self.close()
        
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
    window.show()
    app.exec()
    

if __name__ == '__main__':
    start_app()