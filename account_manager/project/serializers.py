from rest_framework import serializers

from .models import Credential, Project, Task


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = "__all__"
        read_only_fields = ["user"]

    def to_representation(self, model: Meta.model):
        """Represents hashed password as raw password"""
        model.password = model.get_decrypted_password()
        return super().to_representation(model)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["user"]

    credentials = CredentialSerializer(many=True)
    tasks = TaskSerializer(many=True)
