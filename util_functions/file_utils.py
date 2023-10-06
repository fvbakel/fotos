import hashlib
import exifread
import datetime
import os

def get_hash_for_file(filename:str,chunks:True):
    if chunks:
        return _get_hash_for_file_chunks(filename)
    else:
        return _get_hash_for_file_at_once(filename)
       

"""
Function below is a risky incase of a large file, 
but might be faster with small files
"""
def _get_hash_for_file_at_once(filename:str):
    with open(filename, "rb") as f:
        file_hash =  hashlib.md5()
        file_hash.update(f.read())
    return file_hash.hexdigest()

def _get_hash_for_file_chunks(filename:str):
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def get_timestamp_exif(filename:str):
    if not filename.lower().endswith(('jpg','jpeg')):
        return None
    tag = "EXIF DateTimeOriginal"
    with open(filename, "rb") as f:
        tags = exifread.process_file(f,stop_tag = tag)

    if not tag in tags:
        return None
    
    return datetime.datetime.strptime(str(tags[tag]), "%Y:%m:%d %H:%M:%S")

def get_files(path:str,extensions_lower_case:tuple[str]):
    for root, dirs,files in os.walk(path):
        for file in files:
            if file.lower().endswith( extensions_lower_case ):
                yield root, file
        

