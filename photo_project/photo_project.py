from photo_project.model import *
from photo_project.measure import MeasureProgress,MeasureDuration
import file_utils
import pathlib
import time
from datetime import timedelta

"""
For now the peewee based model only supports one active database
so the Photo project has class methods only.

TODO: refactor to singleton

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
        
        measure_md5 = MeasureDuration(autostart=False)
        measure_timestamp = MeasureDuration(autostart=False)
        measure_database_save =MeasureDuration(autostart=False)
        measure = MeasureProgress(total=total)
        for nr,photo in enumerate(query):
            measure_md5.start()
            photo.set_md5_from_file(chunks)
            measure_md5.stop()
            measure_timestamp.start()
            photo.set_timestamp_from_file()
            measure_timestamp.stop()
            measure_database_save.start()
            photo.save()
            measure_database_save.stop()
            if (nr % interval) == 0:
                measure.done = nr
                delta       = timedelta(seconds=round(measure.duration_seconds)) 
                remaining   = timedelta(seconds=round(measure.remaining_estimate_sec))
                print(f'\rProgress: {measure.done_percentage:03.4f}%  speed (photo/sec): {measure.average_speed_nr_per_sec:.1f}  elapsed: {delta} remaining: {remaining} last photo: {photo.path[-20:]}'.ljust(130),end = '')

        measure.stop()
        delta       = timedelta(seconds=round(measure.duration_seconds)) 
        remaining   = timedelta(seconds=round(measure.remaining_estimate_sec))

        print(f'\rProgress: {measure.done_percentage:03.4f}%  speed (photo/sec): {measure.average_speed_nr_per_sec:.1f}  elapsed: {delta} remaining: {remaining} last photo: {photo.path[-20:]}'.ljust(130),end = '')
        print('')
        delta       = timedelta(seconds=round(measure_md5.duration_seconds))
        print(f'The md5 generation took in total {delta}')
        delta       = timedelta(seconds=round(measure_timestamp.duration_seconds))
        print(f'The timestamp extraction took in total {delta}')
        delta       = timedelta(seconds=round(measure_database_save.duration_seconds))
        print(f'The database save took in total {delta}')


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

