from __future__ import annotations

import os
import shlex
import signal
import subprocess
import sys
from typing import TYPE_CHECKING, Any

from celery.app import default_app
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import autoreload
from dotenv import find_dotenv, load_dotenv

from ... import _localization as L  # noqa: TID252, N812

if TYPE_CHECKING:
    from argparse import _ActionsContainer

load_dotenv(find_dotenv())


class Command(BaseCommand):
    """
    https://github.com/Friskes/celery_starter
    """

    help = L.command_help + ' https://github.com/Friskes/celery_starter'

    BASE_DIR = str(settings.BASE_DIR) + os.sep

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
                    #     subprocess.check_call(f"TASKKILL /F /PID {int(line)} /T", **self._std)
                    # except subprocess.CalledProcessError:
                    #     pass

            os.remove(self.BASE_DIR + file_name)

    def run_celery_win(self) -> None:
        """
        Запускает celery[worker/beat/flower] на Windows
        с выводом логов в одну консоль, для локальной разработки.
        """
        # -P --pool
        # prefork  # default (windows not work, linux multiple processes)
        # solo  # (windows/linux single process)
        # threads  # (windows/linux multiple threading) too slow
        # eventlet | gevent  # (windows/linux multiple processes)
        celeryworker_cmd = (
            f"celery -A {self.celery_app} worker -E -l {self.options['loglevel']} -P gevent"
        )
        if self.options['logfile']:
            celeryworker_cmd += f" --logfile={self.options['logfile']}"

        # subprocess.run(
        #     self.command if self.command else shlex.split(celeryworker_cmd)
        # )
        subprocess.Popen(
            self.command if self.command else shlex.split(celeryworker_cmd),
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        if not self.options['beat']:
            self.read_pid_file('celerybeat.pid')
            celerybeat_cmd = f"celery -A {self.celery_app} beat -l {self.options['loglevel']} --pidfile=celerybeat.pid"  # noqa: E501
            # https://docs.celeryq.dev/en/latest/userguide/periodic-tasks.html#using-custom-scheduler-classes
            # celerybeat_cmd += " --scheduler django_celery_beat.schedulers:DatabaseScheduler"
            # celerybeat_cmd += " -S django"
            subprocess.Popen(
                shlex.split(celerybeat_cmd), stdin=subprocess.PIPE, stderr=subprocess.STDOUT
            )

        if not self.options['flower']:
            subprocess.Popen(
                shlex.split(f'celery -A {self.celery_app} flower --url_prefix={self.flower_url_prefix}'),
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
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

        if sys.platform == 'win32':
            self.run_celery_win()
        else:
            subprocess.run(shlex.split(self.command))

    def get_celery_app(self) -> tuple[str, str | None]:
        """
        Возвращает название приложения celery (если находит)
        и команду для запуска worker (если она была передана).
        """
        self.flower_url_prefix = (
            os.environ.get('CELERY_FLOWER_URL_PREFIX', None)
            or getattr(settings, 'CELERY_FLOWER_URL_PREFIX', None)
            or default_app.conf.get('CELERY_FLOWER_URL_PREFIX', 'flower')
        )
        if self.args:
            cmd = self.args[0].split()
            cmd_len = len(cmd)
            if cmd_len == 1:
                return cmd[0], None

            for i in range(cmd_len):
                if cmd[i] == '-A':
                    return cmd[i + 1].strip(), self.args[0]

                if cmd[i].startswith('--app'):
                    return cmd[i].split('=')[-1].strip(), self.args[0]
        else:
            if os.environ.get('CELERY_APP'):
                return os.environ['CELERY_APP'], None

            settings_filename = 'settings.py'
            for root, _dirs, files in os.walk(self.BASE_DIR):
                if settings_filename in files:
                    return root.rsplit('/', 1)[-1], None

        raise ValueError(L.celery_app_not_found)

    def add_arguments(self, parser: _ActionsContainer) -> None:
        """
        Добавляет парсер для аргументов которые попадают в options метода handle.
        """
        parser.add_argument(nargs='*', type=str, dest='args', help=L.proj_name_help)
        parser.add_argument('-b', '--beat', action='store_true', default=False, help=L.beat_help)
        parser.add_argument('-f', '--flower', action='store_true', default=False, help=L.flower_help)
        parser.add_argument('-d', '--debug', action='store_true', default=False, help=L.debug_help)
        parser.add_argument('-ll', '--loglevel', default='INFO', type=str, help=L.log_level)
        parser.add_argument('-lf', '--logfile', default='', type=str, help=L.log_file)

    def handle(self, *args: Any, **options: Any) -> None:
        """
        Срабатывает при первом запуске и изменении любого файла проекта.
        """
        self.args: tuple[str, ...] = args
        self.options = options
        self.celery_app, self.command = self.get_celery_app()

        beat = 'beat ' if not self.options['beat'] else ''
        flower = 'flower ' if not self.options['flower'] else ''

        defails = f"loglevel={self.options['loglevel']}"
        if self.options['logfile']:
            defails += f" logfile={self.options['logfile']}"

        if self.options['debug']:
            msg = L.start_msg % (self.celery_app, beat, flower, defails) + L.debug_msg
        else:
            msg = L.start_msg % (self.celery_app, beat, flower, defails)

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
