from __future__ import annotations

import os
import shlex
import signal
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from celery.app import default_app
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.utils import autoreload
from dotenv import find_dotenv, load_dotenv

from ... import _localization as L  # noqa: TID252, N812

if TYPE_CHECKING:
    from collections.abc import Iterable

load_dotenv(find_dotenv())


CELERY_BEAT_PID_FILENAME = 'celerybeat.pid'


class ConstantNotFoundError(Exception):
    msg = L.constant_not_found

    def __init__(self, constant: str) -> None:
        self.msg = self.msg % constant

    def __str__(self) -> str:
        return self.msg


class ConstructorCommand:
    """"""

    default_worker_cmd = 'celery -A %s worker -E -l INFO -P solo'
    default_beat_cmd = 'celery -A %s beat --pidfile=%s -l INFO'
    default_flower_cmd = 'celery --broker=redis://localhost:6379// flower -A %s --url_prefix=%s'

    @property
    def __celery_app(self) -> str:
        celery_app = os.environ.get('CELERY_APP', None) or getattr(settings, 'CELERY_APP', None)
        if not celery_app and default_app:
            celery_app = default_app.conf.get('CELERY_APP', 'app')

        if not celery_app:
            raise ConstantNotFoundError('CELERY_APP')
        return celery_app

    @property
    def __flower_url_prefix(self) -> str:
        flower_url_prefix = os.environ.get('CELERY_FLOWER_URL_PREFIX', None) or getattr(
            settings, 'CELERY_FLOWER_URL_PREFIX', None
        )
        if not flower_url_prefix and default_app:
            flower_url_prefix = default_app.conf.get('CELERY_FLOWER_URL_PREFIX', 'flower')

        if not flower_url_prefix:
            raise ConstantNotFoundError('CELERY_FLOWER_URL_PREFIX')
        return flower_url_prefix

    @property
    def __flower_broker(self) -> str:
        flower_broker = os.environ.get('CELERY_FLOWER_BROKER', None) or getattr(
            settings, 'CELERY_FLOWER_BROKER', None
        )
        if not flower_broker and default_app:
            flower_broker = default_app.conf.get('CELERY_FLOWER_BROKER', 'flower')

        if not flower_broker:
            raise ConstantNotFoundError('CELERY_FLOWER_BROKER')
        return flower_broker

    def get_celery_app(self, options: Any) -> str:
        celery_app = self.get_flag_value_from_cmd(options['worker'], ['-A', '--app'])
        if not celery_app:
            celery_app = self.get_flag_value_from_cmd(options['beat'], ['-A', '--app'])
        if not celery_app:
            celery_app = self.get_flag_value_from_cmd(options['flower'], ['-A', '--app'])
        if not celery_app:
            celery_app = self.__celery_app
        return celery_app

    def get_flag_value_from_cmd(self, cmd: str, flags: Iterable[str]) -> str:  # type: ignore[return]
        args = shlex.split(cmd)
        for i, arg in enumerate(args):
            if arg.startswith('-'):
                if arg in flags:
                    return args[i + 1]
            elif arg.startswith('--'):
                flag, value = arg.split('=', 1)
                if flag.strip() in flags:
                    return value.strip()

    def cmd_to_dict(self, cmd: str, empty_val: Any = '') -> dict[str, Any]:
        options = {}
        args = shlex.split(cmd)
        special_keywords = ('celery', 'worker', 'beat', 'flower')

        for key, val in zip(args, args[1:] + [empty_val]):  # noqa: B905
            #
            if key in special_keywords:
                options.update({key: ''})
            if val in special_keywords:
                options.update({val: ''})

            if key[0] == '-' and key[1] != '-':
                # print('-key: ', (key, val))
                if val.startswith('-'):
                    options.update({key: empty_val})
                else:
                    options.update({key: val})
            elif key[:2] == '--':
                # print('--key:', (key, val))
                options.update({key: empty_val})

            if val.startswith('-'):
                # print('val:  ', (key, val))
                options.update({val: empty_val})

        return options

    def merge_cmds(self, inputted_cmd: str, default_cmd: str) -> str:
        inputted_opts = self.cmd_to_dict(inputted_cmd)
        default_opts = self.cmd_to_dict(default_cmd)
        merged_opts = dict(default_opts, **inputted_opts)
        return ' '.join(f'{k} {v}' if v else k for k, v in merged_opts.items())

    def construct_worker_cmd(self, cmd: str) -> None:
        """
        -P --pool
        prefork  # default (windows not work, linux multiple processes)
        solo  # (windows/linux single process)
        threads  # (windows/linux multiple threading) too slow
        gevent | eventlet  # (windows/linux multiple processes)
        """
        if not cmd:
            self.worker_cmd = shlex.split(self.default_worker_cmd % self.celery_app)
        elif cmd.startswith('celery'):
            self.worker_cmd = shlex.split(cmd)
        else:
            merged_cmd = self.merge_cmds(cmd, self.default_worker_cmd % self.celery_app)
            self.worker_cmd = shlex.split(merged_cmd)

    def construct_beat_cmd(self, cmd: str) -> None:
        if not cmd:
            self.beat_cmd = shlex.split(
                self.default_beat_cmd % (self.celery_app, CELERY_BEAT_PID_FILENAME)
            )
        elif cmd.startswith('celery'):
            self.beat_cmd = shlex.split(cmd)
        else:
            merged_cmd = self.merge_cmds(
                cmd, self.default_beat_cmd % (self.celery_app, CELERY_BEAT_PID_FILENAME)
            )
            self.beat_cmd = shlex.split(merged_cmd)

    def construct_flower_cmd(self, cmd: str) -> None:
        if not cmd:
            self.flower_cmd = shlex.split(
                self.default_flower_cmd % (self.celery_app, self.__flower_url_prefix)
            )
        elif cmd.startswith('celery'):
            self.flower_cmd = shlex.split(cmd)
        else:
            flower_broker = self.get_flag_value_from_cmd(cmd, ['--broker'])
            if not flower_broker:
                flower_broker = self.__flower_broker

            flower_url_prefix = self.get_flag_value_from_cmd(cmd, ['--url_prefix'])
            if not flower_url_prefix:
                flower_url_prefix = self.__flower_url_prefix

            merged_cmd = self.merge_cmds(
                cmd, self.default_flower_cmd % (self.celery_app, flower_url_prefix)
            )
            self.flower_cmd = shlex.split(merged_cmd)

    def parse_options(self, options: Any) -> None:
        self.celery_app = self.get_celery_app(options)

        self.construct_worker_cmd(options['worker'])
        self.construct_beat_cmd(options['beat'])
        self.construct_flower_cmd(options['flower'])


class Command(BaseCommand):
    """
    https://github.com/Friskes/celery_starter
    """

    help = L.command_help + ' https://github.com/Friskes/celery_starter'

    BASE_DIR = str(settings.BASE_DIR) + os.sep

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.constr = ConstructorCommand()

    def read_pid_file(self, file_name: str) -> None:
        """
        Считывает pid из файла, убивает связанный с ним процесс и удаляет этот файл.
        Файл создается автоматически средствами celery beat
        """
        if file_name in os.listdir(self.BASE_DIR):
            with open(file_name) as file:
                for line in file.readlines():
                    try:
                        os.kill(int(line), signal.SIGTERM)
                    except OSError:
                        pass
                    # try:
                    #     subprocess.check_call(f"TASKKILL /F /T /PID {int(line)}", **self._std)
                    # except subprocess.CalledProcessError:
                    #     pass

            os.remove(self.BASE_DIR + file_name)

    def run_celery(self) -> None:
        """
        Запускает celery[worker/beat/flower]
        с выводом логов в одну консоль. Для локальной разработки.
        """
        subprocess.Popen(self.constr.worker_cmd, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        # subprocess.run(self.constr.worker_cmd)

        if not self.options['exclude_beat']:
            self.read_pid_file(CELERY_BEAT_PID_FILENAME)
            subprocess.Popen(self.constr.beat_cmd, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

        if not self.options['exclude_flower']:
            subprocess.Popen(
                self.constr.flower_cmd,
                stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
            )

    def kill_celery_processes(self) -> None:
        """
        Убивает celery процесс(ы).
        """
        if sys.platform == 'win32':
            subprocess.call(shlex.split('TASKKILL /F /T /IM celery.exe'), **self._std)
            # subprocess.run(["celery", "-A", self.project_name, "control", "shutdown"], **self._std)
        else:
            subprocess.call(shlex.split('pkill celery'), **self._std)

    def reload_celery(self) -> None:
        """
        Убивает процесс(ы) celery если он(и) есть и заного запускает celery.
        """
        self.kill_celery_processes()

        self.run_celery()

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Добавляет парсер для аргументов которые попадают в options метода handle.
        """
        parser.add_argument('-w', '--worker', default='', type=str, help=L.worker_help)
        parser.add_argument('-b', '--beat', default='', type=str, help=L.beat_help)
        parser.add_argument('-f', '--flower', default='', type=str, help=L.flower_help)
        parser.add_argument(
            '-eb', '--exclude_beat', action='store_true', default=False, help=L.exclude_beat_help
        )
        parser.add_argument(
            '-ef', '--exclude_flower', action='store_true', default=False, help=L.exclude_flower_help
        )
        parser.add_argument('-d', '--debug', action='store_true', default=False, help=L.debug_help)

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Срабатывает при первом запуске и изменении любого файла проекта.
        """
        if not hasattr(self.constr, 'celery_app'):
            self.constr.parse_options(options)

        self.options = options

        beat = 'beat ' if not self.options['exclude_beat'] else ''
        flower = 'flower ' if not self.options['exclude_flower'] else ''

        if self.options['debug']:
            msg = L.start_msg % (self.constr.celery_app, beat, flower) + L.debug_msg
        else:
            msg = L.start_msg % (self.constr.celery_app, beat, flower)

        colored_msg = (
            self.style.SUCCESS(msg.split('[')[0].split('(')[0] + '(')
            + self.style.MIGRATE_HEADING(msg.split('[')[0].split('(')[1].split(')')[0])
            + self.style.SUCCESS(') [')
            + self.style.HTTP_SERVER_ERROR(msg.split('[')[1].split(']')[0])
        )
        if self.options['debug']:
            colored_msg += (
                self.style.SUCCESS(']' + msg.split('[')[1].split(']')[1].split('DEBUG')[0])
                + self.style.WARNING('DEBUG')
                + self.style.SUCCESS(msg.split('[')[1].split(']')[1].split('DEBUG')[1])
            )
            self._std: dict[str, Any] = {}
        else:
            colored_msg += self.style.SUCCESS(']' + msg.split('[')[1].split(']')[1])
            self._std = dict(stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        self.stdout.write(colored_msg)

        autoreload.run_with_reloader(self.reload_celery)
