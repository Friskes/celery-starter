import os
import shlex
import subprocess

from . import _localization as L

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import autoreload


# https://habr.com/ru/articles/415049/
# https://testdriven.io/courses/django-celery/auto-reload/
# https://simpleisbetterthancomplex.com/tutorial/2018/08/27/how-to-create-custom-django-management-commands.html
# https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/

BASE_DIR = str(settings.BASE_DIR).replace('\\', '/') + '/'


class Command(BaseCommand):

    help=L.command_help

    def handle(self, *args, **options):
        """Срабатывает при первом запуске и изменении любого файла проекта."""

        self.arguments = args
        self.options = options
        self.project_name = args[0] if args else 'FriskesSite'

        beat = 'beat ' if not self.options['beat'] else ''
        flower = 'flower ' if not self.options['flower'] else ''

        if self.options['debug']:
            msg = L.start_msg % (self.project_name, beat, flower) + L.debug_msg
        else:
            msg = L.start_msg % (self.project_name, beat, flower)

        colored_msg = (self.style.SUCCESS(msg.split('[')[0].split('(')[0] + '(')
                       + self.style.MIGRATE_HEADING(msg.split('[')[0].split('(')[1].split(')')[0])
                       + self.style.SUCCESS(') [')
                       + self.style.HTTP_SERVER_ERROR(msg.split('[')[1].split(']')[0]))
        if self.options['debug']:
            colored_msg += (self.style.SUCCESS(']' + msg.split('[')[1].split(']')[1].split('DEBUG')[0])
                            + self.style.WARNING('DEBUG')
                            + self.style.SUCCESS(msg.split('[')[1].split(']')[1].split('DEBUG')[1]))
        else:
            colored_msg += self.style.SUCCESS(']' + msg.split('[')[1].split(']')[1])

        self.stdout.write(colored_msg)

        autoreload.run_with_reloader(self.restart_celery)


    def add_arguments(self, parser):
        """Добавляет парсер аргументов которые попадут в options метода handle."""

        parser.add_argument(nargs='*', type=str, dest='args', help=L.proj_name_help)
        parser.add_argument('-b', '--beat', action='store_true', default=False, help=L.beat_help)
        parser.add_argument('-f', '--flower', action='store_true', default=False, help=L.flower_help)
        parser.add_argument('-d', '--debug', action='store_true', default=False, help=L.debug_help)


    def restart_celery(self):
        """Убивает все существующие celery процессы и заного запускает их."""

        if self.options['debug']:
            subprocess.call(shlex.split("TASKKILL /F /T /IM celery.exe"))
            # subprocess.run(["celery", "-A", self.project_name, "control", "shutdown"])
        else:
            subprocess.call(
                shlex.split("TASKKILL /F /T /IM celery.exe"),
                stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            # subprocess.run(
            #     ["celery", "-A", self.project_name, "control", "shutdown"],
            #     stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            # )
        self.read_pid_file("celerybeat.pid")

        subprocess.Popen(
            shlex.split(f"celery -A {self.project_name} worker -l info -P eventlet"), # -P solo # -P threads # -P gevent
            stdin=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        if not self.options['beat']:
            # https://docs.celeryq.dev/en/latest/userguide/periodic-tasks.html#using-custom-scheduler-classes
            celerybeat_cmd = f"celery -A {self.project_name} beat -l info --pidfile=celerybeat.pid"
            # celerybeat_cmd += " " + "--scheduler django_celery_beat.schedulers:DatabaseScheduler"
            # celerybeat_cmd += " " + "-S django"
            subprocess.Popen(
                shlex.split(celerybeat_cmd),
                stdin=subprocess.PIPE, stderr=subprocess.STDOUT
            )

        if not self.options['flower']:
            subprocess.Popen(
                shlex.split(f"celery -A {self.project_name} flower --url_prefix=flower"),
                stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )


    def read_pid_file(self, file_name: str):
        """Считывает pid из файла и отправляет его в task_kill_by_pid для удаления процесса."""

        if file_name in os.listdir(BASE_DIR):
            with open(file_name, 'r') as file:

                for line in file.readlines():
                    self.task_kill_by_pid(int(line))

            os.remove(BASE_DIR + file_name)


    def task_kill_by_pid(self, pid: int):
        """Удаляет процесс используя pid."""

        try:
            if self.options['debug']:
                subprocess.check_call("TASKKILL /F /PID {pid} /T".format(pid=pid))
            else:
                subprocess.check_call(
                    "TASKKILL /F /PID {pid} /T".format(pid=pid),
                    stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE
                )
        except subprocess.CalledProcessError:
            pass
