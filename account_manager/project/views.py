from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Credential, Project, Task
from .serializers import CredentialSerializer, ProjectSerializer, TaskSerializer


class BaseListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    model = None

    def get_queryset(self):
        kwargs = {"project__user": self.kwargs.get("user_id"), "project__slug": self.kwargs.get("slug")}
        return self.model.objects.filter(**kwargs)


class BaseRetrieveView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    model = None

    def get_object(self):
        kwargs = {
            "local_id": self.kwargs.get("id"),
            "project__user": self.kwargs.get("user_id"),
            "project__slug": self.kwargs.get("slug"),
        }
        return self.model.objects.get(**kwargs)


class ProjectListView(ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(**self.kwargs)


class ProjectDetailView(RetrieveAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Project.objects.get(**self.kwargs)


class CredentialListView(BaseListView):
    serializer_class = CredentialSerializer
    model = Credential


class CredentialDetailView(BaseRetrieveView):
    serializer_class = CredentialSerializer
    model = Credential


class TaskListView(BaseListView):
    serializer_class = TaskSerializer
    model = Task


class TaskDetailView(BaseRetrieveView):
    serializer_class = TaskSerializer
    model = Task
