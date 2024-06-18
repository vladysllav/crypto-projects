import os

from cryptography.fernet import Fernet
from django.db import models
from django.utils.translation import gettext_lazy as _

from user.models import User


class Project(models.Model):
    title = models.CharField(_("project title"), max_length=255)
    description = models.TextField(_("project description"), null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = models.Manager()
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")

    def __str__(self):
        return f"Title: {self.title}; User: {self.user}"


class Credential(models.Model):
    email = models.EmailField(_("email address"))
    password = models.CharField(_("password"), max_length=128)
    is_new_password = models.BooleanField(_("is new password"), default=True)

    username = models.CharField(_("username"), max_length=150, null=True, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=15, null=True, blank=True)
    service_name = models.CharField(_("service name"), max_length=50)
    login_url = models.URLField(_("login url"), null=True, blank=True)

    objects = models.Manager()
    project: Project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="credentials")

    def __str__(self):
        return f"Service: {self.service_name}; User: {self.project.user}"

    def save(self, *args, **kwargs):
        if self.is_new_password:
            self.set_password()
        super().save(*args, **kwargs)

    @property
    def encryption_key(self):
        return os.getenv("ENCRYPTION_KEY").encode()

    def set_password(self):
        self.is_new_password = False
        cipher_suite = Fernet(self.encryption_key)
        self.password = cipher_suite.encrypt(str(self.password).encode()).decode()

    def get_decrypted_password(self):
        cipher_suite = Fernet(self.encryption_key)
        return cipher_suite.decrypt(self.password.encode()).decode()


class Task(models.Model):
    title = models.CharField(_("task title"), max_length=255)
    description = models.TextField(_("task description"), null=True, blank=True)
    remind_at = models.DateTimeField(_("remind at"), null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = models.Manager()
    project: "Project" = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return f"Title: {self.title}; User: {self.project.user}"
