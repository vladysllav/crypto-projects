from collections import namedtuple as nt

import pytest
from django.urls import reverse
from rest_framework import status

from user.models import User as UserModel

from .conftest import Users

# ----- UserViewSet Test Case Schemas ----------------------------------------------------------------------------------
L_TestCase = nt("List", ["auth_user", "expected_status"])
C_TestCase = nt("Create", ["auth_user", "include_optional_fields", "expected_status"])
R_TestCase = nt("Retrieve", ["auth_user", "user", "expected_status"])
U_TestCase = nt("Update", ["auth_user", "user", "include_optional_fields", "expected_status"])
P_TestCase = nt("PartialUpdate", ["auth_user", "user", "expected_status"])
D_TestCase = nt("Destroy", ["auth_user", "user", "expected_status"])

# ----- UserViewSet Test Cases -----------------------------------------------------------------------------------------
list_user_test_cases = [
    # "auth_user", "expected_status"
    L_TestCase("not_auth", status.HTTP_401_UNAUTHORIZED),
    L_TestCase("admin", status.HTTP_200_OK),
    L_TestCase("user1", status.HTTP_403_FORBIDDEN),
]
create_user_test_cases = [
    # "auth_user", "include_optional_fields", "expected_status"
    C_TestCase("not_auth", False, status.HTTP_201_CREATED),
    C_TestCase("not_auth", True, status.HTTP_201_CREATED),
    C_TestCase("admin", False, status.HTTP_201_CREATED),
    C_TestCase("admin", True, status.HTTP_201_CREATED),
    C_TestCase("user1", False, status.HTTP_403_FORBIDDEN),
]
retrieve_user_test_cases = [
    # "auth_user", "retrieve_user", "expected_status"
    R_TestCase("not_auth", "user1", status.HTTP_401_UNAUTHORIZED),
    R_TestCase("admin", "user1", status.HTTP_200_OK),
    R_TestCase("user1", "user1", status.HTTP_200_OK),
    R_TestCase("user1", "user2", status.HTTP_403_FORBIDDEN),
]
update_user_test_cases = [
    # "auth_user", "update_user", "include_optional_fields", "expected_status"
    U_TestCase("not_auth", "user1", False, status.HTTP_401_UNAUTHORIZED),
    U_TestCase("admin", "user1", False, status.HTTP_200_OK),
    U_TestCase("admin", "user1", True, status.HTTP_200_OK),
    U_TestCase("user1", "user1", False, status.HTTP_200_OK),
    U_TestCase("user1", "user1", True, status.HTTP_200_OK),
    U_TestCase("user1", "user2", False, status.HTTP_403_FORBIDDEN),
]
partial_update_user_test_cases = [
    # "auth_user", "update_user", "expected_status"
    P_TestCase("not_auth", "user1", status.HTTP_401_UNAUTHORIZED),
    P_TestCase("admin", "user1", status.HTTP_200_OK),
    P_TestCase("user1", "user1", status.HTTP_200_OK),
    P_TestCase("user1", "user2", status.HTTP_403_FORBIDDEN),
]
destroy_user_test_cases = [
    # "auth_user", "destroy_user", "expected_status"
    D_TestCase("not_auth", "user1", status.HTTP_401_UNAUTHORIZED),
    D_TestCase("admin", "user1", status.HTTP_204_NO_CONTENT),
    D_TestCase("user1", "user1", status.HTTP_204_NO_CONTENT),
    D_TestCase("user1", "user2", status.HTTP_403_FORBIDDEN),
]


# ----- UserViewSet Tests ----------------------------------------------------------------------------------------------
@pytest.mark.django_db
class TestUserViewSet:

    model = UserModel

    @pytest.fixture(autouse=True)
    def setup_method(self, auth_client, users, testcase_data):
        self.client = auth_client
        self.users: Users = users

        self.create_data = testcase_data.for_create
        self.update_data = testcase_data.for_update
        self.partial_update_data = testcase_data.for_partial_update
        self.optional_fields = testcase_data.optional_fields

    # ----- List User --------------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", list_user_test_cases)
    def test_list_user(self, test_case: L_TestCase):
        client = self.get_testcase_client(test_case)

        url = reverse("user-list")
        response = client.get(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            assert isinstance(response.data, list)
            assert len(response.data) == self.initial_users_count()

    # ----- Create User ------------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", create_user_test_cases)
    def test_create_user(self, test_case: C_TestCase):
        client = self.get_testcase_client(test_case)
        users_count = self.initial_users_count()

        url = reverse("user-list")
        data = self.get_data(self.create_data, test_case.include_optional_fields)
        response = client.post(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_201_CREATED:
            created_user = self.model.objects.get(email=data["email"])

            for field, value in data.items():
                if field != "password":
                    assert getattr(created_user, field) == value

            assert self.model.objects.count() == users_count + 1

    # ----- Retrieve User ----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", retrieve_user_test_cases)
    def test_retrieve_user(self, test_case: R_TestCase):
        client, user = self.get_testcase_client_and_user(test_case)

        url = reverse("user-detail", kwargs={"pk": user.id})
        response = client.get(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            assert response.data.get("email") == user.email

    # ----- Update User ------------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", update_user_test_cases)
    def test_update_user(self, test_case: U_TestCase):
        client, user = self.get_testcase_client_and_user(test_case)

        url = reverse("user-detail", kwargs={"pk": user.id})
        data = self.get_data(self.update_data, test_case.include_optional_fields)
        response = client.put(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            self.verify_user_fields(user.id, data)

    # ----- Partial Update User ----------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", partial_update_user_test_cases)
    def test_partial_update_user(self, test_case: P_TestCase):
        client, user = self.get_testcase_client_and_user(test_case)

        url = reverse("user-detail", kwargs={"pk": user.id})
        data = self.partial_update_data
        response = client.patch(url, data=data)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_200_OK:
            self.verify_user_fields(user.id, data)

    # ----- Destroy User -----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize("test_case", destroy_user_test_cases)
    def test_destroy_user(self, test_case: D_TestCase):
        client, user = self.get_testcase_client_and_user(test_case)
        users_count = self.initial_users_count()

        url = reverse("user-detail", kwargs={"pk": user.id})
        response = client.delete(url)

        assert response.status_code == test_case.expected_status
        if test_case.expected_status == status.HTTP_204_NO_CONTENT:
            assert self.model.objects.filter(id=user.id).first() is None
            assert self.model.objects.count() == users_count - 1

    # ----- Helper Methods ---------------------------------------------------------------------------------------------
    def initial_users_count(self):
        return self.model.objects.count()

    def get_testcase_client(self, test_case):
        return self.client(getattr(self.users, test_case.auth_user))

    def get_testcase_user(self, test_case):
        return getattr(self.users, test_case.user)

    def get_testcase_client_and_user(self, test_case):
        client = self.get_testcase_client(test_case)
        user = self.get_testcase_user(test_case)
        return client, user

    def get_data(self, data: dict, optional_fields: bool = False):
        if optional_fields:
            data.update(self.optional_fields)
        return data

    def verify_user_fields(self, user_id: int, data: dict):
        user = self.model.objects.get(id=user_id)

        for field, value in data.items():
            if field != "password":
                assert getattr(user, field) == value
