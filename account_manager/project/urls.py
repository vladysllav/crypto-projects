from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CredentialViewSet, ProjectViewSet, TaskViewSet

router = DefaultRouter()

list_view = {"get": "list", "post": "create"}
detail_view = {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}

urlpatterns = [
    path("", ProjectViewSet.as_view(list_view), name="project-list"),
    path("<int:project_id>/", ProjectViewSet.as_view(detail_view), name="project-detail"),
    path("<int:project_id>/tasks/", TaskViewSet.as_view(list_view), name="task-list"),
    path("<int:project_id>/tasks/<int:id>/", TaskViewSet.as_view(detail_view), name="task-detail"),
    path("<int:project_id>/credentials/", CredentialViewSet.as_view(list_view), name="credential-list"),
    path("<int:project_id>/credentials/<int:id>/", CredentialViewSet.as_view(detail_view), name="credential-detail"),
]

urlpatterns += router.urls
