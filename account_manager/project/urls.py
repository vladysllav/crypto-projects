from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CredentialDetailView,
    CredentialListView,
    ProjectDetailView,
    ProjectListView,
    TaskDetailView,
    TaskListView,
)

router = DefaultRouter()

urlpatterns = [
    path("", ProjectListView.as_view(), name="project_list"),
    path("<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
    path("<slug:slug>/tasks/", TaskListView.as_view(), name="task_list"),
    path("<slug:slug>/tasks/<int:id>/", TaskDetailView.as_view(), name="task_detail"),
    path("<slug:slug>/credentials/", CredentialListView.as_view(), name="credential_list"),
    path("<slug:slug>/credentials/<int:id>/", CredentialDetailView.as_view(), name="credential_detail"),
]
urlpatterns += router.urls
