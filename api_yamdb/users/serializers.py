from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.common import UserService
from users.constants import MAX_NAMES_STRINGS, MAX_CONFORMATION_CODE_STRING, MAX_EMAIL_STRING
from users.mixin import UsernameValidationMixin
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

        if (
                not user.confirmation_code
                or user.confirmation_code != confirmation_code
        ):
            raise serializers.ValidationError("Неверный код подтверждения")

        user.confirmation_code = ""
        user.save()

        refresh = RefreshToken.for_user(user)
        data["token"] = str(refresh.access_token)

        return data


class SignUpSerializer(serializers.Serializer, UsernameValidationMixin):
    email = serializers.EmailField(max_length=MAX_EMAIL_STRING, required=True)
    username = serializers.CharField(max_length=MAX_NAMES_STRINGS)

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


class UserSerializer(serializers.ModelSerializer, UsernameValidationMixin):
    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "username", "bio", "email", "role"
        )


class UserNoAdminSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ("role",)
