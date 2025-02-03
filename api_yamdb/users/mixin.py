from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UsernameValidationMixin:
    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                _('Пользователь с таким именем уже существует'),
                code='invalid_username'
            )
        return username
