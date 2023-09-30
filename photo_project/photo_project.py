from photo_project.model import *
import file_utils
import pathlib

"""
For now the peewee based model only supports one active database
so the Photo project has class methods only.
"""
class PhotoProject:

    allowed_extensions = ('jpg','jpeg')

    @classmethod
    def set_current_database(cls,db_file:str):
        set_current_database(db_file)

    @classmethod
    def close_current_database(cls):
        close_current_database()

    @classmethod
    def basic_load_basedir(cls,base_dir:BaseDir):
        for root, file in file_utils.get_files(base_dir.base_path,cls.allowed_extensions):
            photo_path = pathlib.Path(root) / pathlib.Path(file)
            photo_sub_path = str(photo_path).removeprefix(base_dir.base_path)[1:]
            Photo.create(base_dir_id=base_dir , path=photo_sub_path,md5='')
            
    @classmethod
    def add_basedir(cls,base_dir_str):
        basedir = BaseDir.create(base_path = base_dir_str)
        cls.basic_load_basedir(basedir)
        return basedir
    
    @classmethod
    def scan_basedir(cls,base_dir:BaseDir):
        photo:Photo
        for photo in Photo.select().where(Photo.base_dir == base_dir):
            photo.set_md5_from_file()
            photo.set_timestamp_from_file()
            photo.save()

    @classmethod
    def get_duplicates(cls):
        duplicate_md5_query = ( Photo
            .select(Photo.md5,fn.GROUP_CONCAT(Photo.full_path).alias('paths'))
            .join(BaseDir, on=(BaseDir.dir_id == Photo.base_dir))
            .group_by(Photo.md5)
            .having(fn.Count(Photo.md5) > 1)
        )

        return duplicate_md5_query

    @classmethod
    def get_duplicates_as_objects(cls):
        duplicate_md5_query = ( Photo
            .select(Photo.md5)
            .group_by(Photo.md5)
            .having(fn.Count(Photo.md5) > 1)
        )
        duplicate_photos_query = ( Photo
            .select()
            .join(duplicate_md5_query,on=(duplicate_md5_query.c.md5 == Photo.md5))
            .order_by(Photo.md5)
        )
        return duplicate_photos_query

