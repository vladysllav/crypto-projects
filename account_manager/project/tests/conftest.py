from collections import namedtuple
from datetime import datetime

import pytest

from tests.conftest import Projects, Users, api_client, auth_client, credentials, projects, users  # noqa: F401

# ----- Data Fixtures --------------------------------------------------------------------------------------------------
DataType = namedtuple("DataType", ["for_create", "for_update", "for_partial_update", "optional_fields"])


@pytest.fixture
def testcase_data():
    data = {
        "project": DataType(
            for_create={"title": "New Project", "is_active": True},
            for_update={"title": "Updated Project", "is_active": True},
            for_partial_update={"title": "New Project Title"},
            optional_fields={"description": "Project Description"},
        ),
        "credential": DataType(
            for_create={
                "email": "user@gmail.com",
                "password": "password",
                "service_name": "Gmail",
            },
            for_update={
                "email": "new_user@gmail.com",
                "password": "new_password",
                "service_name": "Outlook",
            },
            for_partial_update={"email": "new_user@gmail.com", "username": "new_username"},
            optional_fields={"username": "user1", "phone_number": "+380661234567", "login_url": "https://gmail.com"},
        ),
        "task": DataType(
            for_create={"title": "New Task", "is_active": True},
            for_update={"title": "Updated Task", "is_active": False},
            for_partial_update={"description": "New Task Description"},
            optional_fields={"description": "Task Description", "remind_at": datetime.now()},
        ),
    }
    return data
