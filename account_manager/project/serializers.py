from rest_framework import serializers

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
        project_id = self.context["request"].resolver_match.kwargs["project_id"]
        validated_data["project_id"] = project_id
        return super().create(validated_data)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["project"]

    def create(self, validated_data):
        project_id = self.context["request"].resolver_match.kwargs["project_id"]
        validated_data["project_id"] = project_id
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["user", "slug"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class ProjectDetailSerializer(ProjectSerializer):
    credentials = CredentialSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
