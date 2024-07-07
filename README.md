## Django command to run `celery (worker, beat, flower)` with automatically reboot server after changing files

<div align="center">

| Project   |     | Status                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|-----------|:----|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CI/CD     |     | [![Latest Release](https://github.com/Friskes/celery-starter/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/Friskes/celery-starter/actions/workflows/publish-to-pypi.yml)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Quality   |     | [![Coverage](https://codecov.io/github/Friskes/celery-starter/graph/badge.svg?token=vKez4Pycrc)](https://codecov.io/github/Friskes/celery-starter)                                                                                                                                                                                                                                                                                                                               |
| Package   |     | [![PyPI - Version](https://img.shields.io/pypi/v/celery-starter?labelColor=202235&color=edb641&logo=python&logoColor=edb641)](https://badge.fury.io/py/celery-starter) ![PyPI - Support Python Versions](https://img.shields.io/pypi/pyversions/celery-starter?labelColor=202235&color=edb641&logo=python&logoColor=edb641) ![Project PyPI - Downloads](https://img.shields.io/pypi/dm/celery-starter?logo=python&label=downloads&labelColor=202235&color=edb641&logoColor=edb641)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Meta      |     | [![types - Mypy](https://img.shields.io/badge/types-Mypy-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-202235.svg?logo=python&labelColor=202235&color=edb641&logoColor=edb641)](https://spdx.org/licenses/) [![code style - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json&labelColor=202235)](https://github.com/astral-sh/ruff) |

</div>

## Benefits of using this cli
> 1. The ability to run up to three servers (worker, beat, flower) simultaneously in one terminal, instead of running by default in three different terminals.
> 2. Automatic reboot of these servers when your codebase changes

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

### Optional Arguments:
`-h` or `--help` Show help message.<br/>
`-w <cmd>` or `--worker <cmd>` Full command line to run worker or options that extend the default command line.<br/>
`-b <cmd>` or `--beat <cmd>` Full command line to run beat or options that extend the default command line.<br/>
`-f <cmd>` or `--flower <cmd>` Full command line to run flower or options that extend the default command line.<br/>
`-eb` or `--exclude_beat` Excludes the beat server at startup.<br/>
`-ef` or `--exclude_flower` Excludes the flower server at startup.<br/>
`-d` or `--debug` Displays information about successful/unsuccessful completion of processes.<br/>

#### To stopped program pressing the keyboard shortcut `CTRL+C`

### Examples of Commands
> default commands:

```shell
# worker cmd
# (WARNING) Note that the default pool is solo, because of this, all tasks will be performed sequentially, to get parallelism, install one of the libraries [gevent | eventlet] and redefine the default pool in cmd.
celery -A <CELERY_APP> worker -E -l INFO -P solo

# beat cmd
celery -A <CELERY_APP> beat --pidfile=celerybeat.pid -l INFO

# flower cmd
celery --broker=redis://localhost:6379// flower -A <CELERY_APP> --url_prefix=flower
```

> valid commands:
```shell
# redefining the -A and -P parameter and adding a new --broker parameter to the default worker command
python manage.py runcelery -w "-A <CELERY_APP> -P gevent --broker=redis://localhost:6379//"

# complete replacement of the default worker command with the passed command
python manage.py runcelery -w "celery -A <CELERY_APP> worker"
```

#### Working with beat and flower commands works in a similar way.
