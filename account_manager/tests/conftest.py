from collections import namedtuple
from datetime import datetime

import pytest
from rest_framework.test import APIClient

from project.models import Credential as CredentialModel
from project.models import Project as ProjectModel
from project.models import Task as TaskModel
from user.models import User as UserModel


# ----- General Fixtures -----------------------------------------------------------------------------------------------
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    def _auth_client(user=None):
        api_client.force_authenticate(user=user)
        return api_client

    return _auth_client


# ----- User Fixtures -----------------------------------------------------------------------------------------------
Users = namedtuple("Users", ["not_auth", "admin", "user1", "user2"])


@pytest.fixture
def users():
    admin = UserModel.objects.create_superuser("admin", "admin@gmail.com", "password")
    user1 = UserModel.objects.create_user("user1", "user1@gmail.com", "password")
    user2 = UserModel.objects.create_user("user2", "user2@gmail.com", "password")
    return Users(None, admin, user1, user2)


# ----- Project Fixtures -----------------------------------------------------------------------------------------------
Projects = namedtuple("Projects", ["project__user1", "project__user2"])


@pytest.fixture
def projects(users):
    project__user1 = ProjectModel.objects.create(user=users.user1, title="project1", description="first project")
    project__user2 = ProjectModel.objects.create(user=users.user2, title="project1", description="first project")
    return Projects(project__user1, project__user2)


# ----- Credential Fixtures --------------------------------------------------------------------------------------------
Credentials = namedtuple("Credentials", ["cred__project__user1", "cred__project__user2"])


@pytest.fixture
def credentials(projects):
    data = {
        "email": projects.project__user1.user.email,
        "password": "password",
        "service_name": "GitHub",
        "login_url": "https://github.com/login",
    }

    cred__project__user1 = CredentialModel.objects.create(project=projects.project__user1, **data)
    cred__project__user2 = CredentialModel.objects.create(project=projects.project__user2, **data)
    return Credentials(cred__project__user1, cred__project__user2)


# ----- Task Fixtures --------------------------------------------------------------------------------------------------
Tasks = namedtuple("Tasks", ["task__project__user1", "task__project__user2"])


@pytest.fixture
def tasks(projects):
    data = {
        "title": "Task 1",
        "description": "Task Description",
        "remind_at": datetime.now(),
        "is_active": True,
    }

    task__project__user1 = TaskModel.objects.create(project=projects.project__user1, **data)
    task__project__user2 = TaskModel.objects.create(project=projects.project__user2, **data)
    return Tasks(task__project__user1, task__project__user2)
