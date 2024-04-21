## Django command to run `celery (worker, beat, flower)` with automatically reboot server after changing files

## Requirements
- django>=4.2.11
celery>=5.3.6
python-dotenv>=1.0.1

## Install
1. `pip install celery-starter`
2. Add app name to `INSTALLED_APPS`
```python
INSTALLED_APPS = [
    'celery_starter',
]
```

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
--hostname=worker-example@%h
--uid=nobody --gid=nogroup \
--loglevel=INFO" --beat --flower
```
