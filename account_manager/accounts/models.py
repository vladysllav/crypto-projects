import os

from cryptography.fernet import Fernet
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
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
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="credentials")
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
    local_id = models.PositiveIntegerField(editable=False, blank=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="projects")
    slug = models.SlugField(blank=True)

    title = models.CharField(_("project title"), max_length=255)
    description = models.TextField(_("project description"), null=True, blank=True)
    credentials = models.ManyToManyField("Credential", blank=True)
    tasks = models.ManyToManyField("Task", blank=True, related_name="assigned_projects")

    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "slug"], name="unique_slug_per_user"),
            models.UniqueConstraint(fields=["user", "local_id"], name="unique_local_id_per_user")
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug

            counter = 1
            slugs = Project.objects.filter(user=self.user).values_list("slug", flat=True)
            while self.slug in slugs:
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        if not self.local_id:
            self.local_id = generate_local_id(self.__class__, user=self.user)
        super().save(*args, **kwargs)


class Task(models.Model):
    local_id = models.PositiveIntegerField(editable=False, blank=True)
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="project_tasks")

    title = models.CharField(_("task title"), max_length=255)
    description = models.TextField(_("task description"), null=True, blank=True)
    remind_at = models.DateTimeField(_("remind at"), null=True, blank=True)

    objects = models.Manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "local_id"], name="unique_local_id_per_project")
        ]

    def __str__(self):
        return self.title

    def save(self, *args, counter=1, **kwargs):
        if not self.local_id:
            self.local_id = generate_local_id(self.__class__, project=self.project)
        super().save(*args, **kwargs)


def generate_local_id(instance, **kwargs):
    last_instance = instance.objects.filter(**kwargs).order_by("local_id").last()
    return last_instance.local_id + 1 if last_instance else 1
