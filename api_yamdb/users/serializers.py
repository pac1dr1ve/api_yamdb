from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.constants import (
    MAX_NAMES_STRINGS,
    MAX_EMAIL_STRING,
    MAX_CONFORMATION_CODE_STRING,
)
from users.common import UserService
from users.mixin import validate_username_not_me, validate_username
from users.models import User


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=MAX_NAMES_STRINGS)
    confirmation_code = serializers.CharField(
        max_length=MAX_CONFORMATION_CODE_STRING
    )

    def validate(self, data):
        username = data.get("username")
        confirmation_code = data.get("confirmation_code")

        user = get_object_or_404(User, username=username)

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError("Неверный код подтверждения")

        refresh = RefreshToken.for_user(user)
        data["token"] = str(refresh.access_token)

        return data


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=MAX_EMAIL_STRING, required=True)
    username = serializers.CharField(max_length=MAX_NAMES_STRINGS)

    def validate_username(self, value):
        validate_username(value)
        validate_username_not_me(value)
        return value

    def validate(self, data):
        email = data.get("email")
        username = data.get("username")

        user_exists = User.objects.filter(
            models.Q(email=email) | models.Q(username=username))

        if user_exists.exists():
            if user_exists.filter(email=email, username=username).exists():
                return data

        if user_exists.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email уже занят."})

        if user_exists.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "Username уже занят."}
            )

        return data

    def create(self, validated_data):
        user, create = User.objects.get_or_create(**validated_data)
        user.confirmation_code = UserService.create_confirmation_code()
        user.save()
        UserService.send_confirmation_email(user, user.confirmation_code)
        return validated_data


# нужно настроить UserViewSet для выбора сериализатора в зависимости от роли
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "username", "bio", "email", "role"
        )


class UserNoAdminSerializer(UserSerializer):
    role = serializers.CharField(read_only=True)

    class Meta(UserSerializer.Meta):
        pass  # Как ни странно, но нужен pass
