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

        self._args = self._parser.parse_args()

    def run(self):
        self._args.func()

    def _no_args(self):
        self._parser.print_help()

    def _add_basedir(self):
        set_current_database(self._args.project)

        basedir = BaseDir.create(base_path = self._args.dir)

        close_current_database()
