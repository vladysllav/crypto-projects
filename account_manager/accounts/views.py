from rest_framework import viewsets, permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Credential, Project, Task
from .serializers import UserSerializer, CredentialSerializer, ProjectSerializer, TaskSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserSignupView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectListView(ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(**self.kwargs)


class CredentialListView(ListAPIView):
    serializer_class = CredentialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        kwargs = {
            "user_id": self.kwargs.get("user_id"),
            "project__slug": self.kwargs.get("slug")
        }
        creds_id = self.kwargs.get("id")
        kwargs.update({"project__credentials": creds_id}) if creds_id else None
        return Credential.objects.filter(**kwargs)


class TaskListView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        kwargs = {
            "project__slug": self.kwargs.get("slug"),
            "project__user": self.kwargs.get("user_id")
        }
        task_id = self.kwargs.get("id")
        kwargs.update({"local_id": task_id}) if task_id else None
        return Task.objects.filter(**kwargs)
