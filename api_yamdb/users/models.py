from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


ROLES = [
    ('admin', ADMIN),
    ('moderator', MODERATOR),
    ('user', USER)
]


class User(AbstractUser):
    email = models.EmailField(('email address'), unique=True,
                              blank=False, null=False)
    confirmation_code = models.CharField(max_length=100, blank=True)
    username = models.CharField(
        max_length=150,
        verbose_name='Никнейм',
        unique=True,
        blank=False,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Никнейм содержит недопустимы символы!'
            ),
        ],
    )
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(
        max_length=22,
        choices=ROLES,
        default=USER
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER
