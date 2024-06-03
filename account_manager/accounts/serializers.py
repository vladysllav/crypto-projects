from rest_framework import serializers

from .models import User, Credential, Project, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'telegram_id', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = "__all__"
        read_only_fields = ["user"]

    def to_representation(self, model: Meta.model):
        """ Represents hashed password as raw password """
        model.password = model.get_decrypted_password()
        return super().to_representation(model)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    credentials = CredentialSerializer(many=True)
    tasks = TaskSerializer(many=True)

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["user"]
