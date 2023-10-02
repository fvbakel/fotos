from argparse import ArgumentParser
from photo_project import *

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
        parser_2.add_argument("dir_id", help="Id of the base directory",type=int, default=1)
        parser_2.add_argument("-a","--all",help="Recalculate even if the fields is already filled in the database", action='store_true',default=False)
        parser_2.add_argument("-n","--no_chunks",help="Don't calculate the MD5 sum in chunks", action='store_true',default=False)

        parser_2.set_defaults(func=self._scan_basedir)

        parser_3 = sub_parsers.add_parser('get_duplicates',help='Make a list of all the photo\'s that are duplicate based on md5 sum')

        parser_3.set_defaults(func=self._get_duplicates)
        


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
        
