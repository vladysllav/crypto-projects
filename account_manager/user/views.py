from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        objс = get_object_or_404(User, id=self.kwargs.get("pk"))
        if objс.id != self.request.user.id:
            raise PermissionDenied("You do not have permission to see this user.")
        return objс

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You are already logged in.")
        self.permission_classes = [permissions.AllowAny]
        self.check_permissions(self.request)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.permission_classes = [permissions.IsAuthenticated]
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        self.permission_classes = [permissions.IsAuthenticated]
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
