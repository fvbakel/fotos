import sqlite3
import logging
from pathlib import Path
import file_utils
import pathlib

class PhotoProjectDB:

    def __init__(self, db_file: str):
        self.db_file                    = db_file
        self._conn                      = None
        self._open_db()


    def init_tables(self):
        sql = """
            CREATE TABLE parameter (
                name  TEXT NOT NULL UNIQUE,
                value TEXT
            );
        """
        self._conn.execute(sql)

        sql = """
            CREATE TABLE photo (
                photo_id        INTEGER PRIMARY KEY AUTOINCREMENT, 
                base_dir_id     INTEGER,
                path            TEXT,
                md5             TEXT,
                timestamp       TIMESTAMP
            );
        """

        self._conn.execute(sql)

        sql = """
            CREATE TABLE basedir (
                dir_id          INTEGER PRIMARY KEY AUTOINCREMENT, 
                base_path       TEXT
            );
        """

        self._conn.execute(sql)

    def get_parameter(self,parameter:str):
        cursor = self._conn.cursor()
        sql = """   
            SELECT value
            FROM parameter
            where 
                name = ?
        """
        cursor.execute(sql,[parameter])
        rows = cursor.fetchall()

        nr_found = len(rows)
        if  nr_found == 1:
            return rows[0][0]
        elif nr_found == 0:
            logging.info(f'{parameter} not found in parameter table')
            return None
        else:
            logging.error(f'{parameter} found multiple times in parameter table: {nr_found}')
            return None

    def add_parameter(self,parameter:str,value:str):
        cursor = self._conn.cursor()
        sql = """   
            INSERT INTO  parameter values (?,?)
        """
        cursor.execute(sql,[parameter,value])
        self._conn.commit()

    def get_basedir(self,dir_id:int):
        cursor = self._conn.cursor()
        sql = """   
            SELECT base_path
            FROM basedir
            where 
                dir_id = ?
        """
        cursor.execute(sql,[dir_id])
        rows = cursor.fetchall()

        nr_found = len(rows)
        if  nr_found == 1:
            return rows[0][0]
        elif nr_found == 0:
            logging.info(f'{dir_id} not found in basedir table')
            return None
        else:
            logging.error(f'{dir_id} found multiple times in basedir table: {nr_found}')
            return None

    def get_all_basedirs(self):
        cursor = self._conn.cursor()
        sql = """   
            SELECT dir_id,base_path
            FROM basedir
        """
        cursor.execute(sql)
        return cursor.fetchall()

    def add_basedir(self,base_path:str):
        cursor = self._conn.cursor()
        sql = """   
            INSERT INTO  basedir (base_path) values (?)
        """
        cursor.execute(sql,[base_path])
        self._conn.commit()

    def get_photo(self,photo_id:int):
        cursor = self._conn.cursor()
        sql = """   
            SELECT  photo_id,
                    base_dir_id,
                    path,
                    md5,
                    timestamp
            FROM photo
            where 
                photo_id = ?
        """
        cursor.execute(sql,[photo_id])
        rows = cursor.fetchall()

        nr_found = len(rows)
        if  nr_found == 1:
            return rows[0]
        elif nr_found == 0:
            logging.info(f'{photo_id} not found in photo table')
            return None
        else:
            logging.error(f'{photo_id} found multiple times in photo table: {nr_found}')
            return None
    
    def get_photo_on_path(self,base_dir_id:int,path:str):
        cursor = self._conn.cursor()
        sql = """   
            SELECT  photo_id,
                    base_dir_id,
                    path,
                    md5,
                    timestamp
            FROM photo
            where 
                    base_dir_id = ?
                and path = ?
        """
        cursor.execute(sql,[base_dir_id,path])
        rows = cursor.fetchall()

        nr_found = len(rows)
        if  nr_found == 1:
            return rows[0]
        elif nr_found == 0:
            logging.info(f'{path} not found in photo table')
            return None
        else:
            logging.error(f'{path} found multiple times in photo table: {nr_found}')
            return None
        
    def add_photo(self,fields:list):
        cursor = self._conn.cursor()
        sql = """   
            INSERT INTO  photo (base_dir_id,path,md5,timestamp) values (?,?,?,?)
        """
        cursor.execute(sql,fields)
        self._conn.commit()

    def update_photo(self,photo_id:int,fields:list):
        cursor = self._conn.cursor()
        sql = """   
            UPDATE photo 
            SET     base_dir_id = ?,
                    path        = ?,
                    md5         = ?,
                    timestamp   = ?
            WHERE photo_id = ?
        """
        cursor.execute(sql,fields + [photo_id])
        self._conn.commit()

    def _open_db(self):
        self._conn = sqlite3.connect(self.db_file)

    def __del__(self):
        if self._conn:
            self._conn.close()


class BaseDir:
    def __init__(self,dir_id:int,base_path:str):
        self.dir_id:int     = dir_id
        self.path:Path      = Path(base_path)
        self.base_path:str  = str(self.path)


class Photo:
    def __init__(self,base_dir:BaseDir,path:str):
        self.photo_id:int       = 0
        self.base_dir:BaseDir   = base_dir
        self.path:str           = path
        self.md5:str            = ''
        self.timestamp:int      = 0
    
    def read_basic_data(self):
        self.md5 = file_utils.get_hash_for_file(self.full_path)
        self.timestamp = file_utils.get_timestamp_exif(self.full_path)

    @property
    def full_path(self):
        return str(self.base_dir.path / Path(self.path))
    
    @property
    def base_fields(self):
        return [self.base_dir.dir_id,self.path,self.md5,self.timestamp]

class PhotoProject:

    def __init__(self,db:PhotoProjectDB):
        self.db = db
        self._read_base_dirs_from_db()
        self.allowed_extensions = ('jpg','jpeg')

    def _read_base_dirs_from_db(self):
        self.base_dirs:dict[int,BaseDir]        = dict()
        self.base_dirs_path:dict[str,BaseDir]   = dict()
        rows = self.db.get_all_basedirs()
        for row in rows:
            base_dir = BaseDir(row[0],row[1])
            self.base_dirs[row[0]]      = base_dir
            self.base_dirs_path[row[1]] = base_dir

    def get_base_dir(self,dir_id:int):
        return self.base_dirs[dir_id]
    
    def get_base_dir_on_path(self,dir_path:str):
        return self.base_dirs_path[dir_path]
    
    def add_base_dir(self,dir_path:str):
        self.db.add_basedir(dir_path)
        self._read_base_dirs_from_db()
    
    def get_photo(self,photo_id:int):
        fields = self.db.get_photo(photo_id)
        return self.make_photo_from_fields(fields)
    
    def get_photo_on_path(self,base_dir:BaseDir,path:str):
        fields = self.db.get_photo_on_path(base_dir.dir_id,path)
        return self.make_photo_from_fields(fields)
        
    def make_photo_from_fields(self,fields:list):
        if fields is None:
            return None
        if len(fields) < 5:
            return None
        base_dir = self.base_dirs[fields[1]]
        photo = Photo(base_dir,fields[2])
        photo.photo_id       = fields[0]
        photo.md5            = fields[3]
        photo.timestamp      = fields[4]
        return photo
    
    def add_photo(self,photo:Photo):
        self.db.add_photo(photo.base_fields)
        result = self.db.get_photo_on_path(photo.base_dir.dir_id,photo.path)
        if result is None:
            return
        photo.photo_id = result[0]

    def update_photo(self,photo:Photo):
        self.db.update_photo(photo.photo_id,photo.base_fields)

    def basic_load_basedir(self,base_dir:BaseDir):
        for root, file in file_utils.get_files(base_dir.base_path,self.allowed_extensions):
            photo_path = pathlib.Path(root) / pathlib.Path(file)
            photo_sub_path = str(photo_path).removeprefix(base_dir.base_path)[1:]
            photo = Photo(base_dir,photo_sub_path)
            self.add_photo(photo)
