from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


# TODO добавить поле ROLE которое принимает 3 значения
#  (user, moderator, admin). Использовать класс enum.
class Enum:
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


ROLES = [
    (Enum.USER, "User"),
    (Enum.MODERATOR, "Moderator"),
    (Enum.ADMIN, "Admin"),
]


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True, blank=False, null=False)
    groups = models.ManyToManyField(Group, related_name="customer_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="customer_user_permissions")
    confirmation_code = models.CharField(max_length=100, blank=True)
    username = models.CharField(
        max_length=150,
        verbose_name="Никнейм",
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя", blank=True)
    last_name = models.CharField(max_length=150, verbose_name="Фамилия", blank=True)
    bio = models.TextField(verbose_name="Биография", blank=True)
    role = models.CharField(
        max_length=22,
        choices=ROLES,
        default=Enum.USER,
    )

    @property
    def is_admin(self):
        return self.role == Enum.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == Enum.MODERATOR

    @property
    def is_user(self):
        return self.role == Enum.USER