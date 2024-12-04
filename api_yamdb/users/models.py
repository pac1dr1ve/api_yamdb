from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    groups = models.ManyToManyField(Group, related_name="customuser_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_user_permissions")
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
