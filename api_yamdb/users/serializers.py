import re

from rest_framework import serializers

from reviews.models import User


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=10)

    def validate(self, data):
        user = User.objects.get(username=data.get("username"))
        if user.confirmation_code != data.get("confirmation_code"):
            raise serializers.ValidationError("Неверный код подтверждения")
        return data


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.CharField(
        min_length=6,
        max_length=254,
    )
    username = serializers.CharField(
        min_length=4,
        max_length=150,
        required=True,
    )
    first_name = serializers.CharField(
        min_length=4,
        max_length=150,
        required=False,
    )
    last_name = serializers.CharField(
        min_length=4,
        max_length=150,
        required=False
    )
    bio = serializers.CharField(
        required=False
    )
    # TODO использовать enum.role
    role = serializers.CharField(
        required=False
    )

    def validate_username(self, value: str) -> str:
        if value.lower() == "me":
            raise serializers.ValidationError("Недопустимое имя пользователя")
        if not re.fullmatch(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError("Никнейм содержит недопустимы символы!")
        return value


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "bio", "email", "role")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
