import email

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()
user = User.objects.get(email=email)


class User(AbstractUser):
    confirmation_code = models.CharField(max_length=100, blank=True)
    USER = _('user')
    MODERATOR = _('moderator')
    ADMIN = _('admin')

    ROLES = (
        (USER, _('user')),
        (MODERATOR, _('moderator')),
        (ADMIN, _('admin'))
    )

    role = models.CharField(
        max_length=22,
        choices=ROLES,
        default=USER
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER
