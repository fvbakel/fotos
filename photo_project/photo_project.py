from photo_project.model import *
import file_utils
import pathlib

class PhotoProject:

    def __init__(self):

        self.allowed_extensions = ('jpg','jpeg')

    def basic_load_basedir(self,base_dir:BaseDir):
        for root, file in file_utils.get_files(base_dir.base_path,self.allowed_extensions):
            photo_path = pathlib.Path(root) / pathlib.Path(file)
            photo_sub_path = str(photo_path).removeprefix(base_dir.base_path)[1:]
            #Photo.create(base_dir_id=base_dir , path=photo_sub_path,md5='',timestamp = None)
            Photo.create(base_dir_id=base_dir , path=photo_sub_path,md5='')
            
