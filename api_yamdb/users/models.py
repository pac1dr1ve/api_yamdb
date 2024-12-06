from django.contrib.auth.models import AbstractUser, Permission, Group
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
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

    username = models.CharField(
        max_length=254,
        verbose_name='Никнейм',
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message = 'Никнейм содержит недопустимы символы!'
            )
        ],
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя', blank=True)
    last_name = models.CharField(max_length=150, verbose_name='Фамилия', blank=True)
    bio = models.TextField(verbose_name='Биография', blank=True)
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