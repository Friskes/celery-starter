from django.apps import AppConfig


class CeleryStarterConfig(AppConfig):
    name = 'celery_starter'
    verbose_name = 'Django command to launch celery worker, beat, flower'
