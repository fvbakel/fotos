from photo_project.model import *
import file_utils
import pathlib
import time
from datetime import timedelta

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
    def scan_basedir(cls,base_dir:BaseDir,force=False,chunks=True):
        interval = 10
        photo:Photo
        if force:
            query = (Photo.select().where(Photo.base_dir == base_dir))
        else:
            query = (Photo.select().where(Photo.base_dir == base_dir, Photo.md5 == '' ))

        total = query.count()
        print(f'total to scan is: {total}')
        if total == 0:
            return
        
        start = time.time()
        last = start
        for nr,photo in enumerate(query):
            photo.set_md5_from_file(chunks)
            photo.set_timestamp_from_file()
            photo.save()
            if (nr % interval) == 0:
                now = time.time()
                duration = now - start
                progress = ((nr /total)*100)
                average_speed = float(nr) / duration
                nr_todo = total - nr
                if average_speed == 0:
                    average_speed = 0.001
                remaining = timedelta(seconds=round(nr_todo / average_speed))
                delta = timedelta(seconds=round(duration)) 
                
                print(f'\rProgress: {progress:03.4f}%  speed (photo/sec): {average_speed:.1f}  elapsed: {delta} remaining: {remaining} last photo: {photo.path[-20:]}   ',end = '')

        now = time.time()
        duration = now - start
        progress = 100
        remaining = timedelta(seconds=0)
        delta = timedelta(seconds=round(duration)) 
        average_speed = float(total) / duration
        print(f'\rProgress: {progress:03.4f}%  speed (photo/sec): {average_speed:.1f}  elapsed: {delta} remaining: {remaining} last photo: {photo.path[-20:]}   ',end = '')
        print('')


    @classmethod
    def get_duplicates(cls):
        duplicate_md5_query = ( Photo
            .select(Photo.md5,fn.GROUP_CONCAT(Photo.full_path).alias('paths'))
            .join(BaseDir, on=(BaseDir.dir_id == Photo.base_dir))
            .where(Photo.md5 != '')
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

