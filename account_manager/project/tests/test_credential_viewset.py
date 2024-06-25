from collections import namedtuple as nt

import pytest
from django.urls import reverse
from rest_framework import status

from project.models import Credential as CredentialModel

from .conftest import Credentials, Projects, Users

# ----- CredentialViewSet Test Case Schemas ----------------------------------------------------------------------------
L_TestCase = nt("List", ["auth_user", "project", "expected_status"])
C_TestCase = nt("Create", ["auth_user", "project", "include_optional_fields", "expected_status"])
R_TestCase = nt("Retrieve", ["auth_user", "credential", "expected_status"])
U_TestCase = nt("Update", ["auth_user", "credential", "include_optional_fields", "expected_status"])
P_TestCase = nt("PartialUpdate", ["auth_user", "credential", "expected_status"])
D_TestCase = nt("Destroy", ["auth_user", "credential", "expected_status"])

# ----- CredentialViewSet Test Cases -----------------------------------------------------------------------------------
list_credential_test_cases = [
    # "auth_user", "project", "expected_status"
    L_TestCase("not_auth", "project__user1", status.HTTP_401_UNAUTHORIZED),
    L_TestCase("admin", "project__user1", status.HTTP_200_OK),
    L_TestCase("user1", "project__user1", status.HTTP_200_OK),
    L_TestCase("user1", "project__user2", status.HTTP_403_FORBIDDEN),
]
create_credential_test_cases = [
    # "auth_user", "project", "include_optional_fields", "expected_status"
    C_TestCase("not_auth", "project__user1", False, status.HTTP_401_UNAUTHORIZED),
    C_TestCase("admin", "project__user1", False, status.HTTP_201_CREATED),
    C_TestCase("user1", "project__user1", False, status.HTTP_201_CREATED),
    C_TestCase("user1", "project__user1", True, status.HTTP_201_CREATED),
    C_TestCase("user1", "project__user2", False, status.HTTP_403_FORBIDDEN),
]
retrieve_credential_test_cases = [
    # "auth_user", "credential", "expected_status"
    R_TestCase("not_auth", "cred__project__user1", status.HTTP_401_UNAUTHORIZED),
    R_TestCase("admin", "cred__project__user1", status.HTTP_200_OK),
    R_TestCase("user1", "cred__project__user1", status.HTTP_200_OK),
    R_TestCase("user1", "cred__project__user2", status.HTTP_403_FORBIDDEN),
]
update_credential_test_cases = [
    # "auth_user", "credential", "include_optional_fields", "expected_status"
    U_TestCase("not_auth", "cred__project__user1", False, status.HTTP_401_UNAUTHORIZED),
    U_TestCase("admin", "cred__project__user1", False, status.HTTP_200_OK),
    U_TestCase("user1", "cred__project__user1", False, status.HTTP_200_OK),
    U_TestCase("user1", "cred__project__user2", False, status.HTTP_403_FORBIDDEN),
]
partial_update_credential_test_cases = [
    # "auth_user", "credential", "partial_update_data", "expected_status"
    P_TestCase("not_auth", "cred__project__user1", status.HTTP_401_UNAUTHORIZED),
    P_TestCase("admin", "cred__project__user1", status.HTTP_200_OK),
    P_TestCase("user1", "cred__project__user1", status.HTTP_200_OK),
    P_TestCase("user1", "cred__project__user2", status.HTTP_403_FORBIDDEN),
]
destroy_credential_test_cases = [
    # "auth_user", "credential", "expected_status"
    D_TestCase("not_auth", "cred__project__user1", status.HTTP_401_UNAUTHORIZED),
    D_TestCase("admin", "cred__project__user1", status.HTTP_204_NO_CONTENT),
    D_TestCase("user1", "cred__project__user1", status.HTTP_204_NO_CONTENT),
    D_TestCase("user1", "cred__project__user2", status.HTTP_403_FORBIDDEN),
]


# ----- CredentialViewSet Tests ----------------------------------------------------------------------------------------
@pytest.mark.django_db
class TestCredentialViewSet:

    model = CredentialModel

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, auth_client, users, projects, credentials, testcase_data):
        self.client = auth_client
        self.users: Users = users
        self.projects: Projects = projects
        self.credentials: Credentials = credentials

        self.create_data = testcase_data.get("credential").for_create
        self.update_data = testcase_data.get("credential").for_update
        self.partial_update_data = testcase_data.get("credential").for_partial_update
        self.optional_fields = testcase_data.get("credential").optional_fields

    # ----- List Credential --------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", list_credential_test_cases)
    def test_list_credential(self, test_case: L_TestCase):
        client = self.get_testcase_client(test_case)
        project = self.get_testcase_project(test_case)

        path_params = {"user_id": project.user.id, "project_id": project.id}
        url = reverse("credential-list", kwargs=path_params)
        response = client.get(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            assert isinstance(response.data, list)
            assert len(response.data) == self.initial_credential_count(project)

    # ----- Create Credential ------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", create_credential_test_cases)
    def test_create_credential(self, test_case: C_TestCase):
        client = self.get_testcase_client(test_case)
        project = self.get_testcase_project(test_case)
        credentials_count = self.initial_credential_count(project)

        path_params = {"user_id": project.user.id, "project_id": project.id}
        url = reverse("credential-list", kwargs=path_params)
        data = self.get_data(self.create_data, test_case.include_optional_fields)
        response = client.post(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_201_CREATED:
            assert self.model.objects.filter(project=project).count() == credentials_count + 1

    # ----- Retrieve Credential ----------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", retrieve_credential_test_cases)
    def test_retrieve_credential(self, test_case: R_TestCase):
        client, credential = self.get_testcase_client_and_credential(test_case)
        project, user = credential.project, credential.project.user

        path_params = {"user_id": user.id, "project_id": project.id, "id": credential.id}
        url = reverse("credential-detail", kwargs=path_params)
        response = client.get(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            assert response.data.get("email") == credential.email

    # ----- Update Credential ------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", update_credential_test_cases)
    def test_update_credential(self, test_case: U_TestCase):
        client, credential = self.get_testcase_client_and_credential(test_case)
        project, user = credential.project, credential.project.user

        path_params = {"user_id": user.id, "project_id": project.id, "id": credential.id}
        url = reverse("credential-detail", kwargs=path_params)
        data = self.get_data(self.update_data, test_case.include_optional_fields)
        response = client.put(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            self.verify_credential_fields(credential.id, data)

    # ----- Partial Update Credential ----------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", partial_update_credential_test_cases)
    def test_partial_update_credential(self, test_case: P_TestCase):
        client, credential = self.get_testcase_client_and_credential(test_case)
        project, user = credential.project, credential.project.user

        path_params = {"user_id": user.id, "project_id": project.id, "id": credential.id}
        url = reverse("credential-detail", kwargs=path_params)
        data = self.partial_update_data
        response = client.patch(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            self.verify_credential_fields(credential.id, data)

    # ----- Destroy Credential -----------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", destroy_credential_test_cases)
    def test_destroy_credential(self, test_case: D_TestCase):
        client, credential = self.get_testcase_client_and_credential(test_case)
        project, user = credential.project, credential.project.user
        credentials_count = self.initial_credential_count(project)

        path_params = {"user_id": user.id, "project_id": project.id, "id": credential.id}
        url = reverse("credential-detail", kwargs=path_params)
        response = client.delete(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_204_NO_CONTENT:
            assert self.model.objects.filter(id=credential.id).first() is None
            assert self.model.objects.filter(project=project).count() == credentials_count - 1

    # ----- Helper Methods ---------------------------------------------------------------------------------------------
    def initial_credential_count(self, project):
        return self.model.objects.filter(project=project).count()

    def get_testcase_client(self, test_case):
        return self.client(getattr(self.users, test_case.auth_user))

    def get_testcase_project(self, test_case):
        return getattr(self.projects, test_case.project)

    def get_testcase_credential(self, test_case):
        return getattr(self.credentials, test_case.credential)

    def get_testcase_client_and_credential(self, test_case):
        client = self.get_testcase_client(test_case)
        credential = self.get_testcase_credential(test_case)
        return client, credential

    def get_data(self, data: dict, optional_fields: bool = False):
        if optional_fields:
            data.update(self.optional_fields)
        return data

    def verify_credential_fields(self, credential_id: int, data: dict):
        credential = self.model.objects.get(id=credential_id)

        for field, value in data.items():
            if field != "password":
                assert getattr(credential, field) == value
