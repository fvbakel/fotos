# Design of fotos

## Overview

```mermaid
  graph TD;
    photo_project --> util_functions
    photo_project --> model.py
    model.py --> peewee
    model.py --> util_functions
    peewee --> database
    photo_project --> photo_classify   
    photo_gui --> photo_project
    photo_cmd --> photo_project

```

## photo_project

Goal is to have one entry point for all the functionality, independent of the user interface

### Overview of a photo project

```mermaid
  graph LR;
    PhotoProject --> Database(Database:\nDetails of all the photos and configuration)
    PhotoProject --> BaseDirs(BaseDirs:\nDirectories with the actual photo's)
    PhotoProject --> TrainDir(Training directory:\nSmall photo's used for training the model)
    TrainDir --> Person_1
    Person_1 --> TrainPhoto_P1_1.jpg
    Person_1 --> TrainPhoto_P1_2.jpg
    TrainDir --> Person_2
    Person_2 --> TrainPhoto_P2_1.jpg
    Person_2 --> TrainPhoto_P2_2.jpg

    TrainDir --> Person_2

    PhotoProject --> FaceModel(Face model yml file:\nModel file of opencv with the face data)
```

### Database

The database model is based on [peewee-orm](https://docs.peewee-orm.com/)

```mermaid
  classDiagram

    class Parameter {
        name    : str
        value   : str
    }

    class Photo {
        id          : int
        basedir     : int
        md5         : str
        path        : str
        timestamp   : timestamp
    }

    class BaseDir {
        id      : int
        path    : str
    }

    class Person {
        id      : int
        name    : str
    }

    class PhotoPerson {
        photo       : int
        person      : int
        assigned_by : str 
    }

    class Rectangle {
      x       : int
      y       : int
      x_size  : int
      y_size  : int
    }

    class PhotoProcess {
      photo         : int
      process_name  : str
      status        : str
      last_date     : datetime
    }


    Photo --> BaseDir
    Photo --> PhotoPerson
    Photo --> PhotoProcess
    PhotoPerson --> Person
    PhotoPerson --> Rectangle

```

## Photo GUI

```mermaid
  classDiagram

    class MainWindow {
        open_PhotoProject()
        close_PhotoProject()
        update_model()
        scan_basedir()
        view_stats()
        find_photo()
        label_photo()
        find_duplicates()
    }
```
## Todo and ideas

- [ ] New Project function
- [ ] Progress bar
- [ ] Face detect in GUI
- [ ] Scan in GUI
- [X] Log level in separate menu
- [ ] View menu, introduce different views (file list, minuatures)
- [ ] Dockable panels
- [X] Separate query panel, improve search (time, person)
- [ ] Output filename
- [ ] Enable and disable menu items when not applicable
- [ ] Improve duplicates functions
- [ ] Extract and export functions
- [ ] Add processing management dialogs
- [ ] Add other neural network based processing
- [X] Status bar
- [X] Query statistics
- [ ] Add observer pattern for progress
- [ ] Log level in command line
- [ ] On/of face rectangles
- [ ] Detect other objects than faces
- [ ] Manage basedirs
- [ ] Constants for some meaningfull strings
- [ ] Display timestamp and exists in details
