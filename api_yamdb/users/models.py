from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# TODO добавить поле ROLE которое принимает 3 значения
#  (user, moderator, admin). Использовать класс enum.
class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    confirmation_code = models.CharField(max_length=5, blank=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    bio = models.TextField(_("bio"), blank=True)
    role = models.CharField(
        max_length=22,
        choices=[(role.value, role.name) for role in Role],
        default=Role.USER.value,
    )

    @property
    def is_admin(self):
        return self.role == Role.ADMIN.value or self.is_superuser

