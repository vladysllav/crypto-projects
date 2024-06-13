from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Credential, Project, Task
from .serializers import CredentialSerializer, ProjectSerializer, TaskSerializer


class BaseListView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    model = None

    def get_queryset(self):
        kwargs = {"project__user": self.kwargs.get("user_id"), "project__slug": self.kwargs.get("slug")}
        if not kwargs["project__user"] == self.request.user.id:
            raise PermissionDenied("You do not have permission")
        return self.model.objects.filter(**kwargs)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRetrieveView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    model = None

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        kwargs = {
            "local_id": self.kwargs.get("id"),
            "project__user": self.kwargs.get("user_id"),
            "project__slug": self.kwargs.get("slug"),
        }
        if not kwargs["project__user"] == self.request.user.id:
            raise PermissionDenied("You do not have permission.")
        return get_object_or_404(self.model, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectListView(ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.kwargs.get("user_id") == self.request.user.id:
            raise PermissionDenied("You do not have permission")
        return Project.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        try:
            return Project.objects.get(slug=self.kwargs["slug"], user=self.request.user)
        except Project.DoesNotExist:
            raise Http404("Project not found")

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
