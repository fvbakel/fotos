from peewee import *
from playhouse.hybrid import hybrid_property
from util_functions import get_hash_for_file,get_timestamp_exif
import logging

database = SqliteDatabase(None)

def set_current_database(db_file:str):
    database.init(db_file)
    database.connect()
    create_tables()

def close_current_database():
    database.close()

def create_tables():
    database.create_tables([Parameter,BaseDir,Photo,PhotoProcess,Person,PhotoPerson])

class BaseModel(Model):
    class Meta:
        database = database


class Parameter(BaseModel):
    name    = CharField(unique=True),
    value   = CharField()

class BaseDir(BaseModel):
    dir_id      = PrimaryKeyField()
    base_path   = CharField(unique=True)

class Photo(BaseModel):

    photo_id    = PrimaryKeyField()
    base_dir    = ForeignKeyField(BaseDir,backref=None)
    path        = CharField()
    md5         = CharField(null=True)
    timestamp   = DateTimeField(null=True)
    exists      = BooleanField(default=True)

    class Meta:
        indexes = (
            (('base_dir', 'path'), True),
        )
    
    @hybrid_property
    def full_path(self):
        return self.base_dir.base_path + '/' + self.path
    
    def set_md5_from_file(self,chunks=True):
        try:
            self.md5 = get_hash_for_file(self.full_path, chunks)
        except OSError as err:
            logging.error(f'Md5 not updated for {self.full_path}: {str(err)}')

    def set_timestamp_from_file(self):
        try:
            self.timestamp = get_timestamp_exif(self.full_path)
        except OSError as err:
            logging.error(f'Timestamp not updated for {self.full_path}: {str(err)}')
        except ValueError as err:
            logging.error(f'Timestamp not updated for {self.full_path}: {str(err)}')

class PhotoProcess(BaseModel):
    id              = AutoField()
    photo           = ForeignKeyField(Photo,backref=None)
    process_name    = CharField()
    status          = CharField()
    last_date       = DateTimeField(null=True)

    class Meta:
        indexes = (
            (('photo', 'process_name'), True),
        )

class Person(BaseModel):
    person_id   = PrimaryKeyField()
    name        = CharField()

class PhotoPerson(BaseModel):
    id              = AutoField()
    photo           = ForeignKeyField(Photo,backref='persons')
    person          = ForeignKeyField(Person,backref=None,null=True)
    assigned_by     = CharField()
    x               = IntegerField()
    y               = IntegerField()
    w               = IntegerField()
    h               = IntegerField()