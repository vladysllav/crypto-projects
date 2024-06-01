from rest_framework import serializers

from .models import User, Credential, Project, Reminder


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = "__all__"
        read_only_fields = ["user"]

    def to_representation(self, model: Meta.model):
        """ Represents hashed password as raw password """
        model.password = model.get_decrypted_password()
        return super().to_representation(model)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["user"]


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = "__all__"
