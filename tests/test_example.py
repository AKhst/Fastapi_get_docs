# test_check_database.py

import pytest
from .conftest import check_database_exists


def test_database_exists():
    assert (
        check_database_exists()
    ), "Тестовая база данных не существует или нет доступа к ней."
