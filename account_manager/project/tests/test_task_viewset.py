from collections import namedtuple

import pytest
from django.urls import reverse
from rest_framework import status

from project.models import Task as TaskModel

from .conftest import Projects, Tasks, Users

# ----- TaskViewSet Test Case Schemas ----------------------------------------------------------------------------------
ListTestCase = namedtuple("TestCase", ["auth_user", "project", "expected_status"])
CreateTestCase = namedtuple("TestCase", ["auth_user", "project", "include_optional_fields", "expected_status"])
RetrieveTestCase = namedtuple("TestCase", ["auth_user", "task", "expected_status"])
UpdateTestCase = namedtuple("TestCase", ["auth_user", "task", "include_optional_fields", "expected_status"])
PartialUpdateTestCase = namedtuple("TestCase", ["auth_user", "task", "expected_status"])
DestroyTestCase = namedtuple("TestCase", ["auth_user", "task", "expected_status"])

# ----- TaskViewSet Test Cases -----------------------------------------------------------------------------------------
list_task_test_cases = [
    # "auth_user", "project", "expected_status"
    ListTestCase("not_auth", "project__user1", status.HTTP_401_UNAUTHORIZED),
    ListTestCase("admin", "project__user1", status.HTTP_200_OK),
    ListTestCase("user1", "project__user1", status.HTTP_200_OK),
    ListTestCase("user1", "project__user2", status.HTTP_403_FORBIDDEN),
]
create_task_test_cases = [
    # "auth_user", "project", "include_optional_fields", "expected_status"
    CreateTestCase("not_auth", "project__user1", False, status.HTTP_401_UNAUTHORIZED),
    CreateTestCase("admin", "project__user1", False, status.HTTP_201_CREATED),
    CreateTestCase("user1", "project__user1", False, status.HTTP_201_CREATED),
    CreateTestCase("user1", "project__user1", True, status.HTTP_201_CREATED),
    CreateTestCase("user1", "project__user2", False, status.HTTP_403_FORBIDDEN),
]
retrieve_task_test_cases = [
    # "auth_user", "task", "expected_status"
    RetrieveTestCase("not_auth", "task__project__user1", status.HTTP_401_UNAUTHORIZED),
    RetrieveTestCase("admin", "task__project__user1", status.HTTP_200_OK),
    RetrieveTestCase("user1", "task__project__user1", status.HTTP_200_OK),
    RetrieveTestCase("user1", "task__project__user2", status.HTTP_403_FORBIDDEN),
]
update_task_test_cases = [
    # "auth_user", "task", "include_optional_fields", "expected_status"
    UpdateTestCase("not_auth", "task__project__user1", False, status.HTTP_401_UNAUTHORIZED),
    UpdateTestCase("admin", "task__project__user1", False, status.HTTP_200_OK),
    UpdateTestCase("user1", "task__project__user1", False, status.HTTP_200_OK),
    UpdateTestCase("user1", "task__project__user2", False, status.HTTP_403_FORBIDDEN),
]
partial_update_task_test_cases = [
    # "auth_user", "task", "partial_update_data", "expected_status"
    PartialUpdateTestCase("not_auth", "task__project__user1", status.HTTP_401_UNAUTHORIZED),
    PartialUpdateTestCase("admin", "task__project__user1", status.HTTP_200_OK),
    PartialUpdateTestCase("user1", "task__project__user1", status.HTTP_200_OK),
    PartialUpdateTestCase("user1", "task__project__user2", status.HTTP_403_FORBIDDEN),
]
destroy_task_test_cases = [
    # "auth_user", "task", "expected_status"
    DestroyTestCase("not_auth", "task__project__user1", status.HTTP_401_UNAUTHORIZED),
    DestroyTestCase("admin", "task__project__user1", status.HTTP_204_NO_CONTENT),
    DestroyTestCase("user1", "task__project__user1", status.HTTP_204_NO_CONTENT),
    DestroyTestCase("user1", "task__project__user2", status.HTTP_403_FORBIDDEN),
]


# ----- TaskViewSet Tests ----------------------------------------------------------------------------------------------
@pytest.mark.django_db(transaction=True)
class TestTaskViewSet:

    model = TaskModel

    @pytest.fixture(autouse=True)
    def setup_method(self, auth_client, users, projects, tasks, testcase_data):
        self.client = auth_client
        self.users: Users = users
        self.projects: Projects = projects
        self.tasks: Tasks = tasks

        self.create_data = testcase_data.get("task").for_create
        self.update_data = testcase_data.get("task").for_update
        self.partial_update_data = testcase_data.get("task").for_partial_update
        self.optional_fields = testcase_data.get("task").optional_fields

    # ----- List Task --------------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", list_task_test_cases)
    def test_list_task(self, test_case: ListTestCase):
        client = self.get_testcase_client(test_case)
        project = self.get_testcase_project(test_case)

        path_params = {"user_id": project.user.id, "project_id": project.id}
        url = reverse("task-list", kwargs=path_params)
        response = client.get(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            assert isinstance(response.data, list)
            assert len(response.data) == self.initial_task_count(project)

    # ----- Create Task ------------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", create_task_test_cases)
    def test_create_task(self, test_case: CreateTestCase):
        client = self.get_testcase_client(test_case)
        project = self.get_testcase_project(test_case)
        tasks_count = self.initial_task_count(project)

        path_params = {"user_id": project.user.id, "project_id": project.id}
        url = reverse("task-list", kwargs=path_params)
        data = self.get_data(self.create_data, test_case.include_optional_fields)
        response = client.post(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_201_CREATED:
            assert self.model.objects.filter(project=project).count() == tasks_count + 1

    # ----- Retrieve Task ----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", retrieve_task_test_cases)
    def test_retrieve_task(self, test_case: RetrieveTestCase):
        client, task = self.get_testcase_client_and_task(test_case)
        project, user = task.project, task.project.user

        path_params = {"user_id": user.id, "project_id": project.id, "id": task.id}
        url = reverse("task-detail", kwargs=path_params)
        response = client.get(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            assert response.data.get("title") == task.title

    # ----- Update Task ------------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", update_task_test_cases)
    def test_update_task(self, test_case: UpdateTestCase):
        client, task = self.get_testcase_client_and_task(test_case)
        project, user = task.project, task.project.user

        path_params = {"user_id": user.id, "project_id": project.id, "id": task.id}
        url = reverse("task-detail", kwargs=path_params)
        data = self.get_data(self.update_data, test_case.include_optional_fields)
        response = client.put(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            self.verify_task_fields(task.id, data)

    # ----- Partial Update Task ----------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", partial_update_task_test_cases)
    def test_partial_update_task(self, test_case: PartialUpdateTestCase):
        client, task = self.get_testcase_client_and_task(test_case)
        project, user = task.project, task.project.user

        path_params = {"user_id": user.id, "project_id": project.id, "id": task.id}
        url = reverse("task-detail", kwargs=path_params)
        data = self.partial_update_data
        response = client.patch(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            self.verify_task_fields(task.id, data)

    # ----- Destroy Task -----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", destroy_task_test_cases)
    def test_destroy_task(self, test_case: DestroyTestCase):
        client, task = self.get_testcase_client_and_task(test_case)
        project, user = task.project, task.project.user
        tasks_count = self.initial_task_count(project)

        path_params = {"user_id": user.id, "project_id": project.id, "id": task.id}
        url = reverse("task-detail", kwargs=path_params)
        response = client.delete(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_204_NO_CONTENT:
            assert self.model.objects.filter(id=task.id).first() is None
            assert self.model.objects.filter(project=project).count() == tasks_count - 1

    # ----- Helper Methods ---------------------------------------------------------------------------------------------
    def initial_task_count(self, project):
        return self.model.objects.filter(project=project).count()

    def get_testcase_client(self, test_case):
        return self.client(getattr(self.users, test_case.auth_user))

    def get_testcase_project(self, test_case):
        return getattr(self.projects, test_case.project)

    def get_testcase_task(self, test_case):
        return getattr(self.tasks, test_case.task)

    def get_testcase_client_and_task(self, test_case):
        client = self.get_testcase_client(test_case)
        task = self.get_testcase_task(test_case)
        return client, task

    def get_data(self, data: dict, optional_fields: bool = False):
        if optional_fields:
            data.update(self.optional_fields)
        return data

    def verify_task_fields(self, task_id: int, data: dict):
        task = self.model.objects.get(id=task_id)

        for field, value in data.items():
            if field != "password":
                assert getattr(task, field) == value
