from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from reviews.constants import (
    MAX_EMAIL_STRING,
    MAX_CONFORMATION_CODE_STRING,
    MAX_NAMES_STRINGS,
)
from users.validators import (
    validate_username_regex,
    validate_username_me,
)


class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

    def __str__(self):
        return self.name.capitalize()


class User(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
        max_length=MAX_EMAIL_STRING,
    )
    confirmation_code = models.CharField(
        _("Код подтверждения"),
        max_length=MAX_CONFORMATION_CODE_STRING,
        blank=True,
    )
    username = models.CharField(
        _("Никнейм"),
        max_length=MAX_NAMES_STRINGS,
        unique=True,
        validators=(validate_username_regex, validate_username_me)
    )
    first_name = models.CharField(
        _("Имя"),
        max_length=MAX_NAMES_STRINGS,
        blank=True,
    )
    last_name = models.CharField(
        _("Фамилия"),
        max_length=MAX_NAMES_STRINGS,
        blank=True,
    )
    bio = models.TextField(
        _("Биография"),
        blank=True,
    )
    role = models.CharField(
        _("Роль"),
        max_length=max(len(role.value) for role in Role),
        choices=[(role.value, role.name) for role in Role],
        default=Role.USER.value,
    )

    class Meta:
        ordering = ("username", "role",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == Role.ADMIN.value or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == Role.MODERATOR.value
