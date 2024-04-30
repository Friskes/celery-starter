import ctypes
import locale
import sys

if sys.platform == 'win32':
    localization = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
else:
    localization = 'ru_RU'

command_help = """The command launching celery [worker, beat, flower]
 which are automatically restarted when any file is changed"""
start_msg = 'Start celery (%s) [ worker %s%s] %s with function autoreload'
debug_msg = ', in DEBUG mode'
proj_name_help = 'The name of your django project.'
beat_help = 'Excludes the beat server at startup.'
flower_help = 'Excludes the flower server at startup.'
debug_help = 'Displays information about successful/unsuccessful completion of processes.'
log_level = 'Defines the logging level for celery worker/beat'
log_file = 'Redirects the output to the console by default to a log file for celery worker/beat'
celery_app_not_found = (
    'The name of the celery app could not be found, pass the name manually as a positional parameter.'
)

if localization == 'ru_RU':
    command_help = """Команда запускающая celery [worker, beat, flower]
    которые автоматически перезапускаются при изменении любого файла"""
    start_msg = 'Старт celery (%s) [ worker %s%s] %s с функцией autoreload'
    debug_msg = ', в DEBUG режиме'
    proj_name_help = 'Название вашего django проекта.'
    beat_help = 'Исключает beat сервер при запуске.'
    flower_help = 'Исключает flower сервер при запуске.'
    debug_help = 'Отображает информацию о успешном/неудачном завершении процессов.'
    log_level = 'Определяет уровень логирования для celery worker/beat'
    log_file = 'Перенаправляет вывод в консоль по умолчанию в лог файл для celery worker/beat'
    celery_app_not_found = """Не удалось найти название celery приложения,
 передайте название вручную, как позиционный параметр."""
