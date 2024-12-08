import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.models import User


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())],
        required=True,
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Недопустимое имя пользователя")
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

    def validate_first_name(self, value):
        if len(value) > 150:
            raise ValidationError("Имя не должно превышать 150 символов")
        return value

    def validate_last_name(self, value):
        if len(value) > 150:
            raise ValidationError("Фамилия не должна превышать 150 символов")
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', 'user')
        user = User.objects.create(**validated_data, role=role)
        return user


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
            raise ValidationError({'username': 'Пользователь не найден'})


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'email', 'role')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
