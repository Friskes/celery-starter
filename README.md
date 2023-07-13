## Django autoreload adapted for automatic reloading of celery and its modules when changing files in online

### Installing the program

##### Copy the `management` directory and move it to the directory of your application as shown in the diagram

```
Your Project Folder
│
├── <project_name_folder>
│   ├── settings.py
│   ├── wsgi.py
│   └── other files..
├── <application_name_folder>
│   ├── models.py
│   ├── views.py
│   ├── management
│   │   ├── commands
│   │   │   ├── __init__.py
│   │   │   ├── _localization.py
│   │   │   └── runcelery.py
│   │   └── __init__.py
│   └── other files..
└── other folders..
```

### Working with the program

#### Command to run the program: ```python manage.py runcelery <project_name>```

The only mandatory argument is the name of the project.
Arguments can be passed in any order, it doesn't matter.

#### Positional Arguments:
`<project_name>`

#### Optional Arguments:
`-h` Show help message.<br/>
`-b` Excludes the beat server at startup.<br/>
`-f` Excludes the flower server at startup.<br/>
`-d` Displays information about successful/unsuccessful completion of processes.

##### To stopped program pressing the keyboard shortcut CTRL+C
