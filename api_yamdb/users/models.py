from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

def test_validate(value):
    print(f"{value=}")


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    confirmation_code = models.CharField(max_length=5, blank=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=
        [
            # RegexValidator(
            #     regex=r'^[\w.@+-]+$',  # Убрал \Z, заменил на $
            #     message="Можно использовать только буквы, цифры и спецсимволы: ., @, +, -",
            #     code='invalid_username'
            # ),
        test_validate

        ]
    )
    first_name = models.CharField(_("first name"),
                                  max_length=150, blank=True)
    last_name = models.CharField(_("last name"),
                                 max_length=150, blank=True)
    bio = models.TextField(_("Биография"), blank=True)
    role = models.CharField(
        max_length=20,
        choices=[(role.value, role.name) for role in Role],
        default=Role.USER.value,
    )

    @property
    def is_admin(self):
        return self.role == Role.ADMIN.value or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == Role.MODERATOR.value or self.is_superuser

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Пользователи'

        # constraints = [
        #     models.CheckConstraint(
        #         check=models.Q(username__regex=r'^[\w.@+-]+$'),
        #         name='valid_username'
        #     )
        # ]

    def __str__(self):
        return self.username
