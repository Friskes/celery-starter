from src.celery_starter.management.commands.runcelery import Command


# python -m pip install .
# pytest -s ./tests
def test_command() -> None:
    """"""
    cmd = Command()
