from __future__ import annotations

import shlex
from io import StringIO
from unittest import mock

from django.core import management
from django.test import SimpleTestCase
from django.test.utils import override_settings
from src.celery_starter.management.commands.runcelery import (
    CELERY_BEAT_PID_FILENAME,
    Command,
    ConstantNotFoundError,
    ConstructorCommand,
)

override_proj_constants = override_settings(
    CELERY_APP='some_celery_app',
    CELERY_FLOWER_URL_PREFIX='some_flower_url_prefix',
    CELERY_FLOWER_BROKER='some_flower_broker',
)


mocked_run_with_reloader = mock.patch(
    target='celery_starter.management.commands.runcelery.autoreload.run_with_reloader'
)


# pytest -s tests/management/commands/test_constructor_cmd.py::CommandTests::test_cmd_1
class CommandTests(SimpleTestCase):
    default_worker_cmd = shlex.split(ConstructorCommand.default_worker_cmd % 'some_celery_app')
    default_beat_cmd = shlex.split(
        ConstructorCommand.default_beat_cmd
        % (
            'some_celery_app',
            CELERY_BEAT_PID_FILENAME,
        )
    )
    default_flower_cmd = shlex.split(
        ConstructorCommand.default_flower_cmd
        % (
            'some_celery_app',
            'some_flower_url_prefix',
        )
    )

    def setUp(self):
        super().setUp()
        self.out = StringIO()
        self.err = StringIO()
        self.cmd = Command(stdout=self.out, stderr=self.err)

    def call_command(self, *args, **options) -> str:
        splitted_args = (shlex.split(arg) for arg in args)
        return management.call_command(self.cmd, *splitted_args, **options)

    def test_cmd_1(self):
        """Project doesnt have CELERY_APP and CELERY_FLOWER_URL_PREFIX constant."""
        with self.assertRaises(ConstantNotFoundError):
            self.call_command()

    def test_cmd_2(self):
        """Project doesnt have CELERY_FLOWER_URL_PREFIX constant."""
        with override_settings(CELERY_APP='some_celery_app'), self.assertRaises(ConstantNotFoundError):
            self.call_command()

    def test_cmd_3(self):
        """Project doesnt have CELERY_APP constant."""
        with override_settings(CELERY_FLOWER_URL_PREFIX='some_flower_url_prefix'):  # noqa: SIM117
            with self.assertRaises(ConstantNotFoundError):
                self.call_command()

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_4(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and not passing options, cmds must be default.
        """
        self.call_command()

        self.assertEqual(self.cmd.constr.worker_cmd, self.default_worker_cmd)
        self.assertEqual(self.cmd.constr.beat_cmd, self.default_beat_cmd)
        self.assertEqual(self.cmd.constr.flower_cmd, self.default_flower_cmd)

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_5(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and passing custom --worker cmd, all commands except worker should be by default
        """
        input_cmd = 'celery -A some_celery_app worker -E -l WARNING -P gevent'
        self.call_command(f'--worker {input_cmd!r}')

        self.assertEqual(self.cmd.constr.worker_cmd, shlex.split(input_cmd))
        self.assertEqual(self.cmd.constr.beat_cmd, self.default_beat_cmd)
        self.assertEqual(self.cmd.constr.flower_cmd, self.default_flower_cmd)

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_6(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and passing custom --beat cmd, all commands except beat should be by default
        """
        input_cmd = 'celery -A some_celery_app beat --pidfile=celerybeat.pid -l INFO'
        self.call_command(f'--beat {input_cmd!r}')

        self.assertEqual(self.cmd.constr.worker_cmd, self.default_worker_cmd)
        self.assertEqual(self.cmd.constr.beat_cmd, shlex.split(input_cmd))
        self.assertEqual(self.cmd.constr.flower_cmd, self.default_flower_cmd)

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_7(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and passing custom --flower cmd, all commands except flower should be by default
        """
        input_cmd = 'celery --broker=redis://localhost:6379// flower -A some_celery_app --url_prefix=some_flower_url_prefix_2'  # noqa: E501
        self.call_command(f'--flower {input_cmd!r}')

        self.assertEqual(self.cmd.constr.worker_cmd, self.default_worker_cmd)
        self.assertEqual(self.cmd.constr.beat_cmd, self.default_beat_cmd)
        self.assertEqual(self.cmd.constr.flower_cmd, shlex.split(input_cmd))

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_8(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and passing custom --flower, --beat and --flower cmd, all commands must be custom
        """
        input_cmd_worker = 'celery -A some_celery_app_2 worker -E -l WARNING -P gevent'
        input_cmd_beat = 'celery -A some_celery_app_2 beat --pidfile=celerybeat.pid -l INFO'
        input_cmd_flower = 'celery --broker=redis://localhost:6379// flower -A some_celery_app_2 --url_prefix=some_flower_url_prefix_2'  # noqa: E501
        self.call_command(
            f'--worker {input_cmd_worker!r} --beat {input_cmd_beat!r} --flower {input_cmd_flower!r}'
        )

        self.assertEqual(self.cmd.constr.worker_cmd, shlex.split(input_cmd_worker))
        self.assertEqual(self.cmd.constr.beat_cmd, shlex.split(input_cmd_beat))
        self.assertEqual(self.cmd.constr.flower_cmd, shlex.split(input_cmd_flower))

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_9(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and passing additional options for --worker, the worker must expand its flags
        """
        input_options = '--broker=redis://localhost:6379// --result-backend=redis://localhost:6379//'
        self.call_command(f'--worker {input_options!r}')

        self.assertEqual(
            self.cmd.constr.worker_cmd,
            [
                *self.default_worker_cmd,
                *shlex.split(input_options),
            ],
        )

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_10(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and passing additional options for --beat, the beat must expand its flags
        """
        input_options = '--broker=redis://localhost:6379// --result-backend=redis://localhost:6379//'
        self.call_command(f'--beat {input_options!r}')

        self.assertEqual(
            self.cmd.constr.beat_cmd,
            [
                *self.default_beat_cmd,
                *shlex.split(input_options),
            ],
        )

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_11(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and passing additional options for --flower, the flower must expand its flags
        """
        input_options = '--result-backend=redis://localhost:6379// --address=localhost'
        self.call_command(f'--flower {input_options!r}')

        self.assertEqual(
            self.cmd.constr.flower_cmd,
            self.default_flower_cmd + shlex.split(input_options),
        )

    @override_proj_constants
    @mocked_run_with_reloader
    def test_cmd_12(self, mocker: mock.MagicMock):
        """
        Project have all constants
        and passing additional options for --worker,
        the worker must expand its flags and override default flags
        """
        input_options = '-A some_celery_app_2 --broker=redis://localhost:6379// --result-backend=redis://localhost:6379//'
        self.call_command(f'--worker {input_options!r}')

        self.assertEqual(
            self.cmd.constr.worker_cmd,
            [
                'celery',
                '-A',
                'some_celery_app_2',
                'worker',
                '-E',
                '-l',
                'INFO',
                '-P',
                'solo',
                '--broker=redis://localhost:6379//',
                '--result-backend=redis://localhost:6379//',
            ],
        )

    @mocked_run_with_reloader
    def test_cmd_13(self, mocker: mock.MagicMock):
        """
        Passing custom --worker cmd, all commands except worker should be by default,
        but the default beat and flower commands will inherit the -A value from the worker command
        """
        input_cmd = 'celery -A some_celery_app worker -E -l WARNING -P solo'
        with override_settings(CELERY_FLOWER_URL_PREFIX='some_flower_url_prefix'):
            self.call_command(f'--worker {input_cmd!r}')

        self.assertEqual(self.cmd.constr.worker_cmd, shlex.split(input_cmd))
        self.assertEqual(self.cmd.constr.beat_cmd, self.default_beat_cmd)
        self.assertEqual(self.cmd.constr.flower_cmd, self.default_flower_cmd)
