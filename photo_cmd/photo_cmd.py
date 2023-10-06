from argparse import ArgumentParser
from photo_project import *
from util_functions import resize_image
import cv2

class PhotoCommand:

    def __init__(self):
        self._parser = ArgumentParser(description=
            """Command line interface fot the photos functionality
            """
        )
        self._parser.set_defaults(func=self._no_args)
        self._parser.add_argument("-p","--project", help="Name of the photo project database", type=str, required=False, default='photo_project.db')

        sub_parsers = self._parser.add_subparsers()

        parser_1 = sub_parsers.add_parser('add_basedir',help='Add a new base directory to the database')
        parser_1.add_argument("dir", help="Full path of the base directory",type=str, default=None)
        parser_1.set_defaults(func=self._add_basedir)

        parser_2 = sub_parsers.add_parser('scan_basedir',help='Scan a base directory for photos and add these to the database')
        parser_2.add_argument("dir_id", help="Id of the base directory",type=int, default=1,const=1,nargs='?')
        parser_2.add_argument("-a","--all",help="Recalculate even if the fields is already filled in the database", action='store_true',default=False)
        parser_2.add_argument("-n","--no_chunks",help="Don't calculate the MD5 sum in chunks", action='store_true',default=False)
        parser_2.set_defaults(func=self._scan_basedir)

        parser_3 = sub_parsers.add_parser('get_duplicates',help='Make a list of all the photo\'s that are duplicate based on md5 sum')
        parser_3.set_defaults(func=self._get_duplicates)
        
        parser_4 = sub_parsers.add_parser('show_photo',help='Show a photo from the database')
        parser_4.add_argument("photo_id", help="Id of the photo",type=int, default=1)
        parser_4.add_argument("-s","--skip_no_person",help="Skip photo's where no person is detected", action='store_true',default=False)

        parser_4.set_defaults(func=self._show_photo)

        parser_5 = sub_parsers.add_parser('process_photo',help='Run the given process against one or all photos')
        parser_5.add_argument("process", help="Name of the process to run",type=str, default='Exists',choices=['FaceDetect','Exists'],const='Exists',nargs='?')
        parser_5.add_argument("photo_id", help="Id of the photo",type=int, default=1,const=1,nargs='?')
        parser_5.add_argument("-f","--force",help="Force rerun on photo's that are already processed", action='store_true',default=False)
        parser_5.set_defaults(func=self._process_photo)

        self._args = self._parser.parse_args()

    def run(self):
        self._args.func()

    def _no_args(self):
        self._parser.print_help()

    def _add_basedir(self):
        PhotoProject.set_current_database(self._args.project)

        print(f'Adding basedir {self._args.dir}')
        PhotoProject.add_basedir(self._args.dir)
        print('Ready')
        PhotoProject.close_current_database()

    def _scan_basedir(self):
        PhotoProject.set_current_database(self._args.project)
        
        basedir:BaseDir = BaseDir.get_by_id(self._args.dir_id)
        print(f'scanning basedir {basedir.dir_id} : {basedir.base_path}')
        PhotoProject.scan_basedir(base_dir=basedir,force=self._args.all,chunks=not self._args.no_chunks)
        print('Ready')
        PhotoProject.close_current_database()

    def _get_duplicates(self):
        PhotoProject.set_current_database(self._args.project)
        
        print(f'Searching duplicates')
        duplicates = PhotoProject.get_duplicates()
        total = 0
        for duplicate in duplicates:
            print(f'{duplicate.md5}:')
            paths = duplicate.paths.split(',')
            total += len(paths)
            for path in paths:
                print(f'   {path}')
        print(f'total unique photos: {len(duplicates)} number of duplicates: {total}')
        print('Ready')
        PhotoProject.close_current_database()
        
    def _show_photo(self):
        PhotoProject.set_current_database(self._args.project)

        photos = Photo.select().where(Photo.photo_id >= self._args.photo_id)
        for photo in photos:
            if self._args.skip_no_person and len(photo.persons) == 0:
                continue
            
            image = cv2.imread(photo.full_path)
            
            for person in photo.persons:
                cv2.rectangle(image,(person.x,person.y),(person.x+person.w,person.y+person.h),(255,0,0),2)

            image = resize_image(image,width=900)
            #cv2.namedWindow('image window', cv2.WINDOW_NORMAL)
            cv2.imshow('image window', image)
            k = cv2.waitKey(0)
            # 113 is the 'q' key
            if k == -1 or k == 113:
                break

        PhotoProject.close_current_database()
        cv2.destroyAllWindows()

    def _process_photo(self):
        if self._args.process == 'FaceDetect':
            processing = FaceDetect()
        elif self._args.process == 'Exists':
            processing = ExistsProcessing()
        else:
            raise ValueError(f'Error: unexpected process {self._args.process}')

        PhotoProject.set_current_database(self._args.project)

        processing.init_database()
        processing.update_status(Status.NEW,Status.TODO)
        if self._args.force:
            processing.update_status(Status.DONE,Status.TODO)
            processing.update_status(Status.ERROR,Status.TODO)
            processing.update_status(Status.PROCESSING,Status.TODO)

        
        processing.run()

        PhotoProject.close_current_database()