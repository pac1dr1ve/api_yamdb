import re

from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueValidator
from django.core.exceptions import ValidationError

from .models import User


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True
    )

    def validate_username(self, value):

        if not re.fullmatch(r'^[a-zA-Z0-9_]+$', value):
            raise ValidationError("Никнейм содержит недопустимы символы!")

        if len(value) < 4 or len(value) > 150:
            raise ValidationError(
                "Количество символов в никнейме должно быть от 4 до 150"
            )

        return value

    def validate_email(self, value):

        if len(value) < 6 or len(value) > 256:
            raise ValidationError(
                "Количество символов названия почты должно быть от 6 до 256"
            )

        return value


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        try:
            user = User.objects.get(username=username)
            if user.confirmation_code != confirmation_code:
                raise ValidationError(
                    {'confirmation_code': 'Неверный код подтверждения'}
                )
            return {'user': user}
        except User.DoesNotExist:
            raise NotFound({'username': 'Пользователь не найден'})


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')
