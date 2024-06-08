from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=150)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    telegram_id = models.BigIntegerField(_("telegram id"), null=True, blank=True)

    def __str__(self):
        return self.email
