from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .models import Credential, Project, Task
from .serializers import CredentialSerializer, ProjectRetreiveSerializer, ProjectSerializer, TaskSerializer


class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    model = None

    def get_queryset(self):
        kwargs = {"project__user": self.kwargs.get("user_id"), "project_id": self.kwargs.get("project_id")}
        if not kwargs["project__user"] == self.request.user.id:
            raise PermissionDenied("You do not have permission")
        return self.model.objects.filter(**kwargs)

    def get_object(self):
        kwargs = {"project_id": self.kwargs.get("project_id"), "project__user": self.kwargs.get("user_id")}
        if not kwargs["project__user"] == self.request.user.id:
            raise PermissionDenied("You do not have permission.")
        return get_object_or_404(self.model, **kwargs)


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.kwargs.get("user_id") == self.request.user.id:
            raise PermissionDenied("You do not have permissions")
        return Project.objects.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(Project, id=self.kwargs["project_id"], user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProjectRetreiveSerializer
        return ProjectSerializer


class CredentialViewSet(BaseViewSet):
    serializer_class = CredentialSerializer
    model = Credential


class TaskViewSet(BaseViewSet):
    serializer_class = TaskSerializer
    model = Task
