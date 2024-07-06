import ctypes
import locale
import sys

if sys.platform == 'win32':
    localization = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
else:
    localization = None

command_help = """The command launching celery [worker, beat, flower]
 which are automatically restarted when any file is changed"""
start_msg = 'Start celery (%s) [ worker %s%s] with function autoreload'
debug_msg = ', in DEBUG mode'
proj_name_help = 'The name of your django project.'
worker_help = 'Full command line to run worker or options that extend the default command line.'
beat_help = 'Full command line to run beat or options that extend the default command line.'
flower_help = 'Full command line to run flower or options that extend the default command line.'
exclude_beat_help = 'Excludes the beat server at startup.'
exclude_flower_help = 'Excludes the flower server at startup.'
debug_help = 'Displays information about successful/unsuccessful completion of processes.'
constant_not_found = 'The %s constant could not be found in your project.'

if localization == 'ru_RU':
    command_help = """Команда запускающая celery [worker, beat, flower]
 которые автоматически перезапускаются при изменении любого файла"""
    start_msg = 'Старт celery (%s) [ worker %s%s] с функцией autoreload'
    debug_msg = ', в DEBUG режиме'
    proj_name_help = 'Название вашего django проекта.'
    worker_help = """Полная командная строка для запуска worker
 или параметры расширяющие командную строку по умолчанию."""
    beat_help = """Полная командная строка для запуска beat
 или параметры расширяющие командную строку по умолчанию."""
    flower_help = """Полная командная строка для запуска flower
 или параметры расширяющие командную строку по умолчанию."""
    exclude_beat_help = 'Исключает beat сервер при запуске.'
    exclude_flower_help = 'Исключает flower сервер при запуске.'
    debug_help = 'Отображает информацию о успешном/неудачном завершении процессов.'
    constant_not_found = 'Не удалось найти константу %s в вашем проекте.'
