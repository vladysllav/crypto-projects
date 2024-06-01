import os

from cryptography.fernet import Fernet
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=150)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    telegram_id = models.BigIntegerField(_("telegram id"), null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.email


class Credential(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='credentials')
    email = models.EmailField(_("email address"))
    password = models.CharField(_("password"), max_length=128)

    username = models.CharField(_("username"), max_length=150, null=True, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=15, null=True, blank=True)
    service_name = models.CharField(_("service name"), max_length=50)
    login_url = models.URLField(_("login url"), null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"Credentials for {self.service_name}"

    @property
    def encryption_key(self):
        return os.getenv("ENCRYPTION_KEY").encode()

    def set_password(self, raw_password: str):
        cipher_suite = Fernet(self.encryption_key)
        self.password = cipher_suite.encrypt(raw_password.encode()).decode()

    def get_decrypted_password(self):
        cipher_suite = Fernet(self.encryption_key)
        return cipher_suite.decrypt(self.password.encode()).decode()

    def save(self, *args, **kwargs):
        if not self.password.startswith("gAAAAA"):
            self.set_password(self.password)
        super().save(*args, **kwargs)


class Project(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="projects")

    title = models.CharField(_("project title"), max_length=255)
    description = models.TextField(_("project description"), null=True, blank=True)
    credentials = models.ManyToManyField("Credential", blank=True)

    objects = models.Manager()

    def __str__(self):
        return self.title


class Reminder(models.Model):
    project: "Project" = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="reminder_set")
    description = models.TextField(_("reminder description"), null=True, blank=True)
    to_user = models.ManyToManyField("User", blank=True)
    remind_at = models.DateTimeField(_("remind at"))

    objects = models.Manager()

    def __str__(self):
        return f'{self.__class__.__name__} for "{self.project.title}"'
