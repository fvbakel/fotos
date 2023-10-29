from photo_project.model import *
from photo_project.measure import MeasureProgress,MeasureDuration
import util_functions
import pathlib
import time
from datetime import timedelta,datetime
import logging


class PhotoQueryParameters:
    
    STR_OPERATORS = ['Contains','Equal']
    NR_OPERATORS = ['Ignore','Equal','Less than','Greater than']

    def __init__(self):
        self.after: datetime            = None
        self.before: datetime           = None
        self.path: str                  = ''
        self.has_duplicate: bool        = None
        self.is_existing: bool          = None
        
        self.person_name: str           = ''
        self.nr_of_faces: int           = 0
        self.nr_of_persons: int         = 0
        self.assigned_by:str            = ''

        self.path_operator: str             = 'Contains'
        self.nr_of_faces_operator: str      = 'Ignore'
        self.nr_of_persons_operator: str    = 'Ignore'

"""
For now the peewee based model only supports one active database
so the Photo project has class methods only.

TODO: refactor to singleton

"""
class PhotoProject:

    allowed_extensions = ('jpg','jpeg')
    current_db_file = None

    @classmethod
    def set_current_database(cls,db_file:str):
        set_current_database(db_file)
        cls.current_db_file = db_file

    @classmethod
    def close_current_database(cls):
        close_current_database()
        cls.current_db_file = None

    @classmethod
    def get_db_dir(cls):
        if cls.current_db_file is None:
            return None
        return pathlib.Path(cls.current_db_file).parent
        
    @classmethod
    def get_face_recognize_model(cls,recognizer_type:str):
        if cls.current_db_file is None:
            return None
        suffix = f'_face_{recognizer_type}.yml'
        db_path = pathlib.Path(cls.current_db_file)
        db_path_str = str(db_path)
        if not db_path_str.endswith('.db'):
            return db_path_str + suffix
        return db_path_str.replace('.db',suffix)


    @classmethod
    def reload_basedir(cls,base_dir:BaseDir):
        for root, file in util_functions.get_files(base_dir.base_path,cls.allowed_extensions):
            photo_path = pathlib.Path(root) / pathlib.Path(file)
            photo_sub_path = str(photo_path).removeprefix(base_dir.base_path)[1:]
            photo = Photo.get_or_create(base_dir_id=base_dir , path=photo_sub_path)
            #Photo.create(base_dir_id=base_dir , path=photo_sub_path,md5='')
            
    @classmethod
    def add_basedir(cls,base_dir_str):
        basedir = BaseDir.create(base_path = base_dir_str)
        cls.reload_basedir(basedir)
        return basedir
    
    @classmethod
    def scan_basedir(cls,base_dir:BaseDir,force=False,chunks=True):
        interval = 10
        photo:Photo
        if force:
            query = (Photo.select().where(Photo.base_dir == base_dir))
        else:
            query = (Photo.select().where( (Photo.base_dir == base_dir) & (( Photo.md5 == '' ) | Photo.md5.is_null(True) )))

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
    
    @classmethod
    def get_persons(cls):

        photos_with_person_query = ( Photo
            .select()
            .join(PhotoPerson,on=(PhotoPerson.photo == Photo.photo_id))
            .group_by(Photo.photo_id)
        )
        return photos_with_person_query
    
    @classmethod
    def get_recognized(cls):
        photos_with_recognized_person_query = ( Photo
            .select()
            .join(PhotoPerson,on=(PhotoPerson.photo == Photo.photo_id))
            .group_by(Photo.photo_id)
            .where( (PhotoPerson.assigned_by == 'PersonRecognize') )
        )
        return photos_with_recognized_person_query

    
    @staticmethod
    def get_custom(query_parameters:PhotoQueryParameters):
        query = ( Photo
            .select(Photo)
            .join(PhotoPerson,'LEFT JOIN',on=(PhotoPerson.photo == Photo.photo_id))
            .join(Person,'LEFT JOIN',on=(Person.person_id == PhotoPerson.person_id))
            .group_by(Photo.photo_id)
        )

        if query_parameters.assigned_by is not None and query_parameters.assigned_by != '':
            query = query.where( PhotoPerson.assigned_by == query_parameters.assigned_by)
        if query_parameters.person_name is not None and query_parameters.person_name != '':
            query = query.where( Person.name == query_parameters.person_name)
        if query_parameters.path is not None and query_parameters.path != '':
            if query_parameters.path_operator == 'Contains':
                query = query.where( Photo.path.contains(query_parameters.path))
            else:
                query = query.where( Photo.path == query_parameters.path)
        if query_parameters.is_existing is not None:
            query = query.where( Photo.exists == query_parameters.is_existing)

        if query_parameters.after is not None:
            query = query.where( Photo.timestamp >= query_parameters.after)
        if query_parameters.before is not None:
            query = query.where( Photo.timestamp <= query_parameters.before)

        if query_parameters.nr_of_faces_operator == 'Greater than':
            query = query.having( fn.Count(PhotoPerson.id) > query_parameters.nr_of_faces)
        if query_parameters.nr_of_faces_operator == 'Equal':
            query = query.having( fn.Count(PhotoPerson.id) == query_parameters.nr_of_faces)
        if query_parameters.nr_of_faces_operator == 'Less than':
            query = query.having( fn.Count(PhotoPerson.id) < query_parameters.nr_of_faces)

        if query_parameters.nr_of_persons_operator == 'Greater than':
            query = query.having( fn.Count(Person.person_id) > query_parameters.nr_of_persons)
        if query_parameters.nr_of_persons_operator == 'Equal':
            query = query.having( fn.Count(Person.person_id) == query_parameters.nr_of_persons)
        if query_parameters.nr_of_persons_operator == 'Less than':
            query = query.having( fn.Count(Person.person_id) < query_parameters.nr_of_persons)
        if query_parameters.has_duplicate is not None:

            duplicate_md5_query = ( Photo
                .select(Photo.md5)
                .group_by(Photo.md5)
                .having(fn.Count(Photo.md5) > 1)
            )
            if query_parameters.has_duplicate:
                query = query.join(duplicate_md5_query,on=(duplicate_md5_query.c.md5 == Photo.md5))
            else:
                query = query.join(duplicate_md5_query,JOIN.LEFT_OUTER,on=(duplicate_md5_query.c.md5 == Photo.md5))
                query = query.where( duplicate_md5_query.c.md5.is_null())
        logging.info(f'The custom query is: {str(query)}' )
        return query

    @classmethod
    def get_random_photo(cls):
        photo:Photo = Photo.select().order_by(fn.Random()).limit(1).get()
        return photo

