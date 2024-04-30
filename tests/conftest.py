import os

from django.conf import settings


def pytest_configure() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    settings.configure(
        BASE_DIR=base_dir,
    )
