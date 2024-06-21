from collections import namedtuple

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User


# ----- Fixtures -------------------------------------------------------------------------------------------------------
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    def _auth_client(user=None):
        api_client.force_authenticate(user=user) if user else api_client.logout()
        return api_client

    return _auth_client


Data = namedtuple("Data", ["for_create", "for_update", "for_partial_update", "optional"])
Users = namedtuple("Users", ["not_auth", "admin", "user1", "user2"])


@pytest.fixture
def db_data():
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

    optional = {"telegram_id": 1234}
    return Data(for_create, for_update, for_partial_update, optional)


@pytest.fixture
def db_users():
    admin = User.objects.create_superuser("admin", "admin@gmail.com", "password")
    user1 = User.objects.create_user("user1", "user1@gmail.com", "password")
    user2 = User.objects.create_user("user2", "user2@gmail.com", "password")
    return Users(None, admin, user1, user2)


# ----- Test Cases -----------------------------------------------------------------------------------------------------
ListTestCase = namedtuple("TestCase", ["auth_user", "expected_status"])
CreateTestCase = namedtuple("TestCase", ["auth_user", "include_optional_fields", "expected_status"])
RetrieveTestCase = namedtuple("TestCase", ["auth_user", "retrieve_user", "expected_status"])
UpdateTestCase = namedtuple("TestCase", ["auth_user", "update_user", "include_optional_fields", "expected_status"])
PartialUpdateTestCase = namedtuple("TestCase", ["auth_user", "update_user", "expected_status"])
DestroyTestCase = namedtuple("TestCase", ["auth_user", "destroy_user", "expected_status"])

list_user_test_cases = [
    # "auth_user", "expected_status"
    ListTestCase("not_auth", status.HTTP_401_UNAUTHORIZED),
    ListTestCase("admin", status.HTTP_200_OK),
    ListTestCase("user1", status.HTTP_403_FORBIDDEN),
]

create_user_test_cases = [
    # "auth_user", "include_optional_fields", "expected_status"
    (CreateTestCase("not_auth", False, status.HTTP_201_CREATED)),
    (CreateTestCase("not_auth", True, status.HTTP_201_CREATED)),
    (CreateTestCase("admin", False, status.HTTP_201_CREATED)),
    (CreateTestCase("admin", True, status.HTTP_201_CREATED)),
    (CreateTestCase("user1", False, status.HTTP_400_BAD_REQUEST)),
]

retrieve_user_test_cases = [
    # "auth_user", "retrieve_user", "expected_status"
    (RetrieveTestCase("not_auth", "user1", status.HTTP_401_UNAUTHORIZED)),
    (RetrieveTestCase("admin", "user1", status.HTTP_200_OK)),
    (RetrieveTestCase("user1", "user1", status.HTTP_200_OK)),
    (RetrieveTestCase("user1", "user2", status.HTTP_403_FORBIDDEN)),
]
update_user_test_cases = [
    # "auth_user", "update_user", "include_optional_fields", "expected_status"
    (UpdateTestCase("not_auth", "user1", False, status.HTTP_401_UNAUTHORIZED)),
    (UpdateTestCase("admin", "user1", False, status.HTTP_200_OK)),
    (UpdateTestCase("admin", "user1", True, status.HTTP_200_OK)),
    (UpdateTestCase("user1", "user1", False, status.HTTP_200_OK)),
    (UpdateTestCase("user1", "user1", True, status.HTTP_200_OK)),
    (UpdateTestCase("user1", "user2", False, status.HTTP_403_FORBIDDEN)),
]

partial_update_user_test_cases = [
    # "auth_user", "update_user", "expected_status"
    (PartialUpdateTestCase("not_auth", "user1", status.HTTP_401_UNAUTHORIZED)),
    (PartialUpdateTestCase("admin", "user1", status.HTTP_200_OK)),
    (PartialUpdateTestCase("user1", "user1", status.HTTP_200_OK)),
    (PartialUpdateTestCase("user1", "user2", status.HTTP_403_FORBIDDEN)),
]

destroy_user_test_cases = [
    # "auth_user", "destroy_user", "expected_status"
    (DestroyTestCase("not_auth", "user1", status.HTTP_401_UNAUTHORIZED)),
    (DestroyTestCase("admin", "user1", status.HTTP_204_NO_CONTENT)),
    (DestroyTestCase("user1", "user1", status.HTTP_204_NO_CONTENT)),
    (DestroyTestCase("user1", "user2", status.HTTP_403_FORBIDDEN)),
]


# ----- Tests for UserViewSet ------------------------------------------------------------------------------------------
@pytest.mark.django_db(transaction=True)
class TestUserViewSet:

    model = User

    @pytest.mark.parametrize("test_case", list_user_test_cases)
    def test_list_user(self, auth_client, test_case: ListTestCase, db_users: Users):
        client = auth_client(getattr(db_users, test_case.auth_user))
        response = client.get(reverse("user-list"))
        assert response.status_code == test_case.expected_status

        if test_case.expected_status == status.HTTP_200_OK:
            assert isinstance(response.data, list)
            assert len(response.data) == self.initial_users_count()

    @pytest.mark.parametrize("test_case", create_user_test_cases)
    def test_create_user(self, auth_client, test_case: CreateTestCase, db_users: Users, db_data: Data):
        client = auth_client(getattr(db_users, test_case.auth_user))
        users_count = self.initial_users_count()
        data = db_data.for_create.copy()

        if test_case.include_optional_fields:
            data.update(db_data.optional)

        response = client.post(reverse("user-list"), data=data)
        assert response.status_code == test_case.expected_status

        if test_case.expected_status == status.HTTP_201_CREATED:
            created_user = self.model.objects.get(email=data["email"])

            for field, value in data.items():
                if field != "password":
                    assert getattr(created_user, field) == value

            assert self.model.objects.count() == users_count + 1

    @pytest.mark.parametrize("test_case", retrieve_user_test_cases)
    def test_retrieve_user(self, auth_client, test_case: RetrieveTestCase, db_users: Users):
        client = auth_client(getattr(db_users, test_case.auth_user))
        user = getattr(db_users, test_case.retrieve_user)

        response = client.get(reverse("user-detail", kwargs={"pk": user.pk}))
        assert response.status_code == test_case.expected_status

        if test_case.expected_status == status.HTTP_200_OK:
            assert response.data.get("email") == user.email

    @pytest.mark.parametrize("test_case", update_user_test_cases)
    def test_update_user(self, auth_client, test_case: UpdateTestCase, db_users: Users, db_data: Data):
        client = auth_client(getattr(db_users, test_case.auth_user))
        user = getattr(db_users, test_case.update_user)
        data = db_data.for_update.copy()

        if test_case.include_optional_fields:
            data.update(db_data.optional)

        response = client.put(reverse("user-detail", kwargs={"pk": user.pk}), data=data)
        assert response.status_code == test_case.expected_status
        self.verify_update(user, data, test_case.expected_status)

    @pytest.mark.parametrize("test_case", partial_update_user_test_cases)
    def test_partial_update_user(self, auth_client, test_case: PartialUpdateTestCase, db_users: Users, db_data: Data):
        client = auth_client(getattr(db_users, test_case.auth_user))
        user = getattr(db_users, test_case.update_user)
        data = db_data.for_partial_update

        response = client.patch(reverse("user-detail", kwargs={"pk": user.pk}), data=data)
        assert response.status_code == test_case.expected_status
        self.verify_update(user, data, test_case.expected_status)

    @pytest.mark.parametrize("test_case", destroy_user_test_cases)
    def test_destroy_user(self, auth_client, test_case: DestroyTestCase, db_users: Users):
        client = auth_client(getattr(db_users, test_case.auth_user))
        user = getattr(db_users, test_case.destroy_user)
        users_count = self.initial_users_count()

        response = client.delete(reverse("user-detail", kwargs={"pk": user.pk}))
        assert response.status_code == test_case.expected_status

        if test_case.expected_status == status.HTTP_204_NO_CONTENT:
            assert self.model.objects.filter(pk=user.pk).first() is None
            assert self.model.objects.count() == users_count - 1

    # ----- Helper Methods ---------------------------------------------------------------------------------------------
    def initial_users_count(self):
        return self.model.objects.count()

    def verify_update(self, user, data, expected_status):
        if expected_status == status.HTTP_200_OK:
            updated_user = self.model.objects.get(pk=user.pk)
            for field, value in data.items():
                if field != "password":
                    assert getattr(updated_user, field) == value
