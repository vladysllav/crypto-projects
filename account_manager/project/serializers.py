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
        read_only_fields = ["project"]

    def create(self, validated_data):
        slug = self.context["request"].resolver_match.kwargs["slug"]
        project = Project.objects.get(slug=slug, user=self.context["request"].user)
        task = Task.objects.create(project=project, **validated_data)
        return task


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["user", "slug"]

    credentials = CredentialSerializer(many=True, required=False)
    tasks = TaskSerializer(many=True, required=False)

    def create(self, validated_data):
        user = self.context["request"].user
        project = Project.objects.create(user=user, **validated_data)
        return project
