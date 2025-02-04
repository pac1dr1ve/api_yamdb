from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UsernameValidationMixin:
    username_validator = RegexValidator(
        regex=r"^[\w.@+_-]+\Z",
        message="Можно использовать только буквы "
                "(включая буквы в верхнем и нижнем регистрах), "
                "цифры и спецсимволы: ., @, +, - ",
        code="invalid_username",
    )

    def validate_username(self, username):
        self.username_validator(username)
        if username.lower() == 'me':
            raise serializers.ValidationError(
                _('Пользователь с таким именем уже существует'),
                code='invalid_username'
            )
        return username
