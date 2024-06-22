from collections import namedtuple

import pytest
from django.urls import reverse
from rest_framework import status

from project.models import Project as ProjectModel

from .conftest import Projects, Users

# ----- ProjectViewSet Test Case Schemas -------------------------------------------------------------------------------
ListTestCase = namedtuple("TestCase", ["auth_user", "user", "expected_status"])
CreateTestCase = namedtuple("TestCase", ["auth_user", "user", "include_optional_fields", "expected_status"])
RetrieveTestCase = namedtuple("TestCase", ["auth_user", "project", "expected_status"])
UpdateTestCase = namedtuple("TestCase", ["auth_user", "project", "include_optional_fields", "expected_status"])
PartialUpdateTestCase = namedtuple("TestCase", ["auth_user", "project", "expected_status"])
DestroyTestCase = namedtuple("TestCase", ["auth_user", "project", "expected_status"])

# ----- ProjectViewSet Test Cases --------------------------------------------------------------------------------------
list_project_test_cases = [
    # "auth_user", "user", "expected_status"
    ListTestCase("not_auth", "user1", status.HTTP_401_UNAUTHORIZED),
    ListTestCase("admin", "admin", status.HTTP_404_NOT_FOUND),
    ListTestCase("admin", "user1", status.HTTP_200_OK),
    ListTestCase("user1", "user1", status.HTTP_200_OK),
    ListTestCase("user1", "user2", status.HTTP_403_FORBIDDEN),
]
create_project_test_cases = [
    # "auth_user", "user", "include_optional_fields", "expected_status"
    CreateTestCase("not_auth", "user1", False, status.HTTP_401_UNAUTHORIZED),
    CreateTestCase("admin", "user1", False, status.HTTP_201_CREATED),
    CreateTestCase("user1", "user1", False, status.HTTP_201_CREATED),
    CreateTestCase("user1", "user1", True, status.HTTP_201_CREATED),
    CreateTestCase("user1", "user2", False, status.HTTP_403_FORBIDDEN),
]
retrieve_project_test_cases = [
    # "auth_user", "project", "expected_status"
    RetrieveTestCase("not_auth", "project__user1", status.HTTP_401_UNAUTHORIZED),
    RetrieveTestCase("admin", "project__user1", status.HTTP_200_OK),
    RetrieveTestCase("user1", "project__user1", status.HTTP_200_OK),
    RetrieveTestCase("user1", "project__user2", status.HTTP_403_FORBIDDEN),
]
update_project_test_cases = [
    # "auth_user", "project", "include_optional_fields", "expected_status"
    UpdateTestCase("not_auth", "project__user1", False, status.HTTP_401_UNAUTHORIZED),
    UpdateTestCase("admin", "project__user1", False, status.HTTP_200_OK),
    UpdateTestCase("user1", "project__user1", False, status.HTTP_200_OK),
    UpdateTestCase("user1", "project__user2", False, status.HTTP_403_FORBIDDEN),
]
partial_update_project_test_cases = [
    # "auth_user", "project", "expected_status"
    PartialUpdateTestCase("not_auth", "project__user1", status.HTTP_401_UNAUTHORIZED),
    PartialUpdateTestCase("admin", "project__user1", status.HTTP_200_OK),
    PartialUpdateTestCase("user1", "project__user1", status.HTTP_200_OK),
    PartialUpdateTestCase("user1", "project__user2", status.HTTP_403_FORBIDDEN),
]
destroy_project_test_cases = [
    # "auth_user", "project", "expected_status"
    DestroyTestCase("not_auth", "project__user1", status.HTTP_401_UNAUTHORIZED),
    DestroyTestCase("admin", "project__user1", status.HTTP_204_NO_CONTENT),
    DestroyTestCase("user1", "project__user1", status.HTTP_204_NO_CONTENT),
    DestroyTestCase("user1", "project__user2", status.HTTP_403_FORBIDDEN),
]


# ----- ProjectViewSet Tests -------------------------------------------------------------------------------------------
@pytest.mark.django_db(transaction=True)
class TestProjectViewSet:
    model = ProjectModel

    @pytest.fixture(autouse=True)
    def setup_method(self, auth_client, users, projects, testcase_data):
        self.client = auth_client
        self.users: Users = users
        self.projects: Projects = projects

        self.create_data = testcase_data.get("project").for_create
        self.update_data = testcase_data.get("project").for_update
        self.partial_update_data = testcase_data.get("project").for_partial_update
        self.optional_fields = testcase_data.get("project").optional_fields

    # ----- List Project -----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", list_project_test_cases)
    def test_list_project(self, test_case: ListTestCase):
        client, user = self.get_testcase_client_and_user(test_case)

        url = reverse("project-list", kwargs={"user_id": user.id})
        response = client.get(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            assert isinstance(response.data, list)
            assert len(response.data) == self.initial_project_count(user)

    # ----- Create Project ---------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", create_project_test_cases)
    def test_create_project(self, test_case: CreateTestCase):
        client, user = self.get_testcase_client_and_user(test_case)
        projects_count = self.initial_project_count(user)

        url = reverse("project-list", kwargs={"user_id": user.id})
        data = self.get_data(self.create_data, test_case.include_optional_fields)
        response = client.post(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_201_CREATED:
            assert self.model.objects.filter(user=user).count() == projects_count + 1

    # ----- Retrieve Project -------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", retrieve_project_test_cases)
    def test_retrieve_project(self, test_case: RetrieveTestCase):
        client, project = self.get_testcase_client_and_project(test_case)

        url = reverse("project-detail", kwargs={"user_id": project.user.id, "project_id": project.id})
        response = client.get(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            assert response.data.get("title") == project.title

    # ----- Update Project ---------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", update_project_test_cases)
    def test_update_project(self, test_case: UpdateTestCase):
        client, project = self.get_testcase_client_and_project(test_case)

        url = reverse("project-detail", kwargs={"user_id": project.user.id, "project_id": project.id})
        data = self.get_data(self.update_data, test_case.include_optional_fields)
        response = client.put(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            self.verify_project_fields(project.id, data)

    # ----- Partial Update Project -------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", partial_update_project_test_cases)
    def test_partial_update_project(self, test_case: PartialUpdateTestCase):
        client, project = self.get_testcase_client_and_project(test_case)

        url = reverse("project-detail", kwargs={"user_id": project.user.id, "project_id": project.id})
        data = self.partial_update_data
        response = client.patch(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            self.verify_project_fields(project.id, data)

    # ----- Destroy Project --------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", destroy_project_test_cases)
    def test_destroy_project(self, test_case: DestroyTestCase):
        client, project = self.get_testcase_client_and_project(test_case)
        projects_count = self.initial_project_count(project.user)

        url = reverse("project-detail", kwargs={"user_id": project.user.id, "project_id": project.id})
        response = client.delete(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_204_NO_CONTENT:
            assert self.model.objects.filter(id=project.id).first() is None
            assert self.model.objects.filter(user=project.user).count() == projects_count - 1

    # ----- Helper Methods ---------------------------------------------------------------------------------------------
    def initial_project_count(self, user):
        return self.model.objects.filter(user=user).count()

    def get_testcase_client(self, test_case):
        return self.client(getattr(self.users, test_case.auth_user))

    def get_testcase_user(self, test_case):
        return getattr(self.users, test_case.user)

    def get_testcase_project(self, test_case):
        return getattr(self.projects, test_case.project)

    def get_testcase_client_and_user(self, test_case):
        client = self.get_testcase_client(test_case)
        user = self.get_testcase_user(test_case)
        return client, user

    def get_testcase_client_and_project(self, test_case):
        client = self.get_testcase_client(test_case)
        project = self.get_testcase_project(test_case)
        return client, project

    def get_data(self, data: dict, optional_fields: bool = False):
        if optional_fields:
            data.update(self.optional_fields)
        return data

    def verify_project_fields(self, project_id: int, data: dict):
        project = self.model.objects.get(id=project_id)
        for field, value in data.items():
            assert getattr(project, field) == value
