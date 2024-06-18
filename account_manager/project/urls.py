from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CredentialViewSet, ProjectViewSet, TaskViewSet

router = DefaultRouter()

list_view = {"get": "list", "post": "create"}
detail_view = {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}

urlpatterns = [
    path("", ProjectViewSet.as_view(list_view), name="project_list"),
    path("<int:project_id>/", ProjectViewSet.as_view(detail_view), name="project_detail"),
    path("<int:project_id>/tasks/", TaskViewSet.as_view(list_view), name="task_list"),
    path("<int:project_id>/tasks/<int:id>/", TaskViewSet.as_view(detail_view), name="task_detail"),
    path("<int:project_id>/credentials/", CredentialViewSet.as_view(list_view), name="credential_list"),
    path("<int:project_id>/credentials/<int:id>/", CredentialViewSet.as_view(detail_view), name="credential_detail"),
]

urlpatterns += router.urls
