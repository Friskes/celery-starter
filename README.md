## Django command created to run `celery (worker, beat, flower)` with one command and to automatically reboot servers after changing files

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

### Dependencies
- python-dotenv
- psutil

### Working with the program

#### Command to run the program:
```
python manage.py runcelery
```

Arguments can be passed in any order, it doesn't matter.

#### Positional Arguments:
`<celery app name>`
or
`<"full command to run celery worker">`

#### Optional Arguments:
`-h` or `--help` Show help message.<br/>
`-b` or `--beat` Excludes the beat server at startup.<br/>
`-f` or `--flower` Excludes the flower server at startup.<br/>
`-d` or `--debug` Displays information about successful/unsuccessful completion of processes.<br/>
`-ll` or `--loglevel` Defines the logging level for celery worker/beat
`-lf` or `--logfile` Redirects the output to the console by default to a log file for celery worker/beat

##### To stopped program pressing the keyboard shortcut `CTRL+C`

### Examples of Commands
The command enclosed in quotation marks gets into the positional arguments and replaces the command to run the default celery worker.
The `--beat` `--flower` commands fall into the optional arguments and turn off the beat and flower of the server.
```shell script
python manage.py runcelery "celery --app=${CELERY_APP} worker -E \
--statedb=/var/run/celery/worker-example@%h.state \
--hostname=worker-example@%h --uid=nobody --gid=nogroup \
--loglevel=INFO \
--logfile=/var/log/celery/worker-example.log" --beat --flower
```
