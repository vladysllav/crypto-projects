from collections import namedtuple

import pytest

from tests.conftest import Users, api_client, auth_client, django_db_setup, users  # noqa: F401

# ----- Data Fixtures --------------------------------------------------------------------------------------------------
Data = namedtuple("Data", ["for_create", "for_update", "for_partial_update", "optional_fields"])


@pytest.fixture
def testcase_data():
    for_create = {
        "username": "john_doe",
        "email": "john.doe@gmail.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
    }

    for_update = {
        "username": "jane_doe",
        "email": "jane.doe@gmail.com",
        "password": "newpassword",
        "first_name": "Jane",
        "last_name": "Doe",
    }

    for_partial_update = {"email": "jane_doe_new@gmail.com"}

    optional_fields = {"telegram_id": 1234}
    return Data(for_create, for_update, for_partial_update, optional_fields)
