from collections import namedtuple
from datetime import datetime

import pytest
from rest_framework.test import APIClient

from project.models import Credential as CredentialModel
from project.models import Project as ProjectModel
from project.models import Task as TaskModel
from user.models import User as UserModel

# ----- Schemas --------------------------------------------------------------------------------------------------------
Users = namedtuple("Users", ["not_auth", "admin", "user1", "user2"])
Projects = namedtuple("Projects", ["project__user1", "project__user2"])
Credentials = namedtuple("Credentials", ["cred__project__user1", "cred__project__user2"])
Tasks = namedtuple("Tasks", ["task__project__user1", "task__project__user2"])


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


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: django_db_setup
    with django_db_blocker.unblock():
        if not is_db_data():
            create_test_data()


# ----- User Fixtures --------------------------------------------------------------------------------------------------
@pytest.fixture
def users():
    db_users = UserModel.objects.all()
    admin = db_users.get(username="admin")
    user1 = db_users.get(username="user1")
    user2 = db_users.get(username="user2")
    return Users(None, admin, user1, user2)


# ----- Project Fixtures -----------------------------------------------------------------------------------------------
@pytest.fixture
def projects(users):
    all_projects = ProjectModel.objects.all()
    project__user1 = all_projects.get(user=users.user1)
    project__user2 = all_projects.get(user=users.user2)
    return Projects(project__user1, project__user2)


# ----- Credential Fixtures --------------------------------------------------------------------------------------------
@pytest.fixture
def credentials(projects):
    all_credentials = CredentialModel.objects.all()
    cred__project__user1 = all_credentials.get(project=projects.project__user1)
    cred__project__user2 = all_credentials.get(project=projects.project__user2)
    return Credentials(cred__project__user1, cred__project__user2)


# ----- Task Fixtures --------------------------------------------------------------------------------------------------
@pytest.fixture
def tasks(projects):
    all_tasks = TaskModel.objects.all()
    task__project__user1 = all_tasks.get(project=projects.project__user1)
    task__project__user2 = all_tasks.get(project=projects.project__user2)
    return Tasks(task__project__user1, task__project__user2)


# ----- Data -----------------------------------------------------------------------------------------------------------
def create_test_data():
    users = create_users()
    projects = create_projects(users)
    create_credentials(projects)
    create_tasks(projects)


def is_db_data():
    return bool(list(UserModel.objects.all()))


def create_users():
    admin = UserModel.objects.create_superuser("admin", "admin@gmail.com", "password")
    user1 = UserModel.objects.create_user("user1", "user1@gmail.com", "password")
    user2 = UserModel.objects.create_user("user2", "user2@gmail.com", "password")
    return Users(None, admin, user1, user2)


def create_projects(users):
    project__user1 = ProjectModel.objects.create(user=users.user1, title="project1", description="first project")
    project__user2 = ProjectModel.objects.create(user=users.user2, title="project1", description="first project")
    return Projects(project__user1, project__user2)


def create_credentials(projects):
    data = {
        "email": projects.project__user1.user.email,
        "password": "password",
        "service_name": "GitHub",
        "login_url": "https://github.com/login",
    }

    CredentialModel.objects.create(project=projects.project__user1, **data)
    CredentialModel.objects.create(project=projects.project__user2, **data)


def create_tasks(projects):
    data = {
        "title": "Task 1",
        "description": "Task Description",
        "remind_at": datetime.now(),
        "is_active": True,
    }

    TaskModel.objects.create(project=projects.project__user1, **data)
    TaskModel.objects.create(project=projects.project__user2, **data)
