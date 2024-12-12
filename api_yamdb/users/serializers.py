import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from typing import Dict, Any

from reviews.models import User


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(max_length=50, required=True)

    def validate(self, data: Dict[str, str]) -> Dict[str, Any]:
        username = data["username"]
        confirmation_code = data["confirmation_code"]
        if len(confirmation_code) != 50:
            raise serializers.ValidationError("Неверный формат кода подтверждения")
        try:
            user = User.objects.get(username=username)
            if user.confirmation_code != confirmation_code:
                raise ValidationError(
                    {"confirmation_code": "Неверный код подтверждения"},
                )
            return {"user": user}
        except User.DoesNotExist:
            raise serializers.ValidationError({"username": "Пользователь не найден"})


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
    )

    def validate_first_name(self, value):
        if len(value) < 4 or len(value) > 150:
            raise serializers.ValidationError("Имя должно быть от 4 до 150 символов")
        return value

    def validate_last_name(self, value):
        if len(value) < 4 or len(value) > 150:
            raise serializers.ValidationError("Фамилия должна быть от 4 до 150 символов")
        return value

    def validate_username(self, value: str) -> str:
        if value.lower() == "me":
            raise serializers.ValidationError("Недопустимое имя пользователя")
        if not re.fullmatch(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError("Никнейм содержит недопустимы символы!")
        if 4 > len(value) > 150:
            raise serializers.ValidationError(
                "Количество символов в никнейме должно быть от 4 до 150",
            )
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким "
                                              "username уже существует")
        return value

    def validate_email(self, value):
        if 6 > len(value) > 256:
            raise serializers.ValidationError(
                "Количество символов названия почты должно быть от 6 до 256",
            )
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким "
                                              "email уже существует")
        return value


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "bio", "email", "role")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
