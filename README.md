## Django command to run `celery (worker, beat, flower)` with automatically reboot server after changing files

<div align="center">

| Project   |     | Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|-----------|:----|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CI/CD     |     | [![Latest Release](https://github.com/Friskes/celery-starter/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/Friskes/celery-starter/actions/workflows/publish-to-pypi.yml)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Quality   |     | [![Coverage](https://codecov.io/github/Friskes/celery-starter/graph/badge.svg?token=vKez4Pycrc)](https://codecov.io/github/Friskes/celery-starter)                                                                                                                                                                                                                                                                                                                               |
| Package   |     | [![PyPI - Version](https://img.shields.io/pypi/v/celery-starter?labelColor=202235&color=edb641&logo=python&logoColor=edb641)](https://badge.fury.io/py/celery-starter) ![PyPI - Support Python Versions](https://img.shields.io/pypi/pyversions/celery-starter?labelColor=202235&color=edb641&logo=python&logoColor=edb641) ![Project PyPI - Downloads](https://img.shields.io/pypi/dm/celery-starter?logo=python&label=downloads&labelColor=202235&color=edb641&logoColor=edb641)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Meta      |     | [![types - Mypy](https://img.shields.io/badge/types-Mypy-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://spdx.org/licenses/) [![code style - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json&labelColor=202235)](https://github.com/astral-sh/ruff) |

</div>

## Install
1. Install package
    ```bash
    pip install celery-starter
    ```

2. Add app name to `INSTALLED_APPS`
    ```python
    INSTALLED_APPS = [
        'celery_starter',
    ]
    ```

### Command to run the program:
```
python manage.py runcelery
```

Arguments can be passed in any order, it doesn't matter.

### Positional Arguments:
`<celery app name>`
or
`<"full command to run celery worker">`

### Optional Arguments:
`-h` or `--help` Show help message.<br/>
`-b` or `--beat` Excludes the beat server at startup.<br/>
`-f` or `--flower` Excludes the flower server at startup.<br/>
`-d` or `--debug` Displays information about successful/unsuccessful completion of processes.<br/>
`-ll` or `--loglevel` Defines the logging level for celery worker/beat
`-lf` or `--logfile` Redirects the output to the console by default to a log file for celery worker/beat

#### To stopped program pressing the keyboard shortcut `CTRL+C`

### Examples of Commands
The command enclosed in quotation marks gets into the positional arguments and replaces the command to run the default celery worker.
The `--beat` `--flower` commands fall into the optional arguments and turn off the beat and flower of the server.
```shell script
python manage.py runcelery "celery --app=${CELERY_APP} worker -E \
--hostname=worker-example@%h
--uid=nobody --gid=nogroup \
--loglevel=INFO" --beat --flower
```
