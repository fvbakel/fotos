import hashlib
import exifread
import datetime
import os

def get_hash_for_file(filename:str):
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def get_timestamp_exif(filename:str):
    if not filename.lower().endswith(('jpg','jpeg')):
        return 0
    tag = "EXIF DateTimeOriginal"
    with open(filename, "rb") as f:
        tags = exifread.process_file(f,stop_tag = tag)

    if not tag in tags:
        return 0
    
    return datetime.datetime.strptime(str(tags[tag]), "%Y:%m:%d %H:%M:%S").timestamp()
    


def get_files(path:str,extensions_lower_case:tuple[str]):
    for root, dirs,files in os.walk(path):
        for file in files:
            if file.lower().endswith( extensions_lower_case ):
                yield root, file
        
