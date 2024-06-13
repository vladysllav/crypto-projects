from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CredentialViewSet, ProjectViewSet, TaskViewSet

router = DefaultRouter()

urlpatterns = [
    path("", ProjectViewSet.as_view({"get": "list", "post": "create"}), name="project_list"),
    path(
        "<slug:slug>/",
        ProjectViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="project_detail",
    ),
    path("<slug:slug>/tasks/", TaskViewSet.as_view({"get": "list", "post": "create"}), name="task_list"),
    path(
        "<slug:slug>/tasks/<int:id>/",
        TaskViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="task_detail",
    ),
    path(
        "<slug:slug>/credentials/",
        CredentialViewSet.as_view({"get": "list", "post": "create"}),
        name="credential_list",
    ),
    path(
        "<slug:slug>/credentials/<int:id>/",
        CredentialViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="credential_detail",
    ),
]
urlpatterns += router.urls
