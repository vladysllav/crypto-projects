import os

from cryptography.fernet import Fernet
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from user.models import User


class Manager(models.Manager):

    def generate_local_id(self, **kwargs):
        last_instance = self.model.objects.filter(**kwargs).order_by("local_id").last()
        return last_instance.local_id + 1 if last_instance else 1

    def generate_slug(self, title, counter=1, **kwargs):
        slugs = self.model.objects.filter(**kwargs).values_list("slug", flat=True)
        slug = slugify(title)
        original_slug = slug

        while slug in slugs:
            slug = f"{original_slug}-{counter}"
            counter += 1
        return slug


class Project(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "slug"], name="unique_project_slug_per_user"),
            models.UniqueConstraint(fields=["user", "local_id"], name="unique_project_id_per_user"),
        ]

    slug = models.SlugField(blank=True)
    local_id = models.PositiveIntegerField(editable=False, blank=True)

    title = models.CharField(_("project title"), max_length=255)
    description = models.TextField(_("project description"), null=True, blank=True)

    objects = Manager()
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")

    def __str__(self):
        return f"Title: {self.title}; User: {self.user}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.set_slug()

        if not self.local_id:
            self.set_local_id()

        super().save(*args, **kwargs)

    def set_slug(self):
        self.slug = Project.objects.generate_slug(title=self.title, user=self.user)

    def set_local_id(self):
        self.local_id = Project.objects.generate_local_id(user=self.user)


class Credential(models.Model):
    class Meta:
        constraints = [models.UniqueConstraint(fields=["project", "local_id"], name="unique_credential_id_per_project")]

    local_id = models.PositiveIntegerField(editable=False, blank=True)

    email = models.EmailField(_("email address"))
    password = models.CharField(_("password"), max_length=128)
    is_new_password = models.BooleanField(_("is new password"), default=True)

    username = models.CharField(_("username"), max_length=150, null=True, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=15, null=True, blank=True)
    service_name = models.CharField(_("service name"), max_length=50)
    login_url = models.URLField(_("login url"), null=True, blank=True)

    objects = Manager()
    project: Project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="credentials")

    def __str__(self):
        return f"Service: {self.service_name}; User: {self.project.user}"

    def save(self, *args, **kwargs):
        if self.is_new_password:
            self.set_password()

        if not self.local_id:
            self.set_local_id()

        super().save(*args, **kwargs)

    @property
    def encryption_key(self):
        return os.getenv("ENCRYPTION_KEY").encode()

    def set_local_id(self):
        self.local_id = Credential.objects.generate_local_id(project=self.project)

    def set_password(self):
        self.is_new_password = False
        cipher_suite = Fernet(self.encryption_key)
        self.password = cipher_suite.encrypt(str(self.password).encode()).decode()

    def get_decrypted_password(self):
        cipher_suite = Fernet(self.encryption_key)
        return cipher_suite.decrypt(self.password.encode()).decode()


class Task(models.Model):
    class Meta:
        constraints = [models.UniqueConstraint(fields=["project", "local_id"], name="unique_task_id_per_project")]

    local_id = models.PositiveIntegerField(editable=False, blank=True)
    title = models.CharField(_("task title"), max_length=255)
    description = models.TextField(_("task description"), null=True, blank=True)
    remind_at = models.DateTimeField(_("remind at"), null=True, blank=True)

    objects = Manager()
    project: "Project" = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return f"Title: {self.title}; User: {self.project.user}"

    def save(self, *args, counter=1, **kwargs):
        if not self.local_id:
            self.set_local_id()

        super().save(*args, **kwargs)

    def set_local_id(self):
        self.local_id = Task.objects.generate_local_id(project=self.project)
