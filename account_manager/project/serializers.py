from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Credential, Project, Task


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = "__all__"
        read_only_fields = ["project"]

    def to_representation(self, model: Meta.model):
        """Represents hashed password as raw password"""
        model.password = model.get_decrypted_password()
        return super().to_representation(model)

    def create(self, validated_data):
        kwargs = {"slug": self.context["request"].resolver_match.kwargs["slug"], "user": self.context["request"].user}
        project = get_object_or_404(Project, **kwargs)
        validated_data["project"] = project
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["project"]

    def create(self, validated_data):
        kwargs = {"slug": self.context["request"].resolver_match.kwargs["slug"], "user": self.context["request"].user}
        project = get_object_or_404(Project, **kwargs)
        validated_data["project"] = project
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["user", "slug", "credentials", "tasks"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
