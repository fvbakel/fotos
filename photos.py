from photo_cmd import PhotoCommand
from photo_gui import start_app
import sys

def main():

    if len(sys.argv) == 1:
        start_app()
    else:
        command = PhotoCommand()
        command.run()


if __name__ == '__main__':  
    main()