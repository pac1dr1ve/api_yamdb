from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import User


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=5)

    def validate(self, data):
        user = User.objects.get(username=data.get("username"))
        if user.confirmation_code != data.get("confirmation_code"):
            raise serializers.ValidationError("Неверный код подтверждения")
        return data


class SignUpSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True, min_length=8, required=False)
    email = serializers.EmailField(
        min_length=6, max_length=254, required=True)
    username_validator = RegexValidator(
        r"^[\w.@+-]+\Z",
        message="Никнейм содержит недопустимы символы!",
    )
    username = serializers.CharField(min_length=4, max_length=150,
                                     validators=[username_validator])
    first_name = serializers.CharField(
        min_length=4,
        max_length=150,
        required=False,
    )
    last_name = serializers.CharField(
        min_length=4, max_length=150, required=False)
    bio = serializers.CharField(required=False)

    def validate_username(self, value):
        if value.lower() == "me":
            raise serializers.ValidationError("Недопустимое имя пользователя")
        return value

    def validate(self, data):
        email = data.get("email")
        username = data.get("username")

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if user_by_email and user_by_email == user_by_username:
            return data

        if user_by_email and user_by_username:
            raise serializers.ValidationError(
                {"email": "Email уже занят.", "username": "Username уже занят."},
            )

        if user_by_email:
            raise serializers.ValidationError({"email": "Email уже занят."})

        if user_by_username:
            raise serializers.ValidationError({"username": "Username уже занят."})

        return data


class UserSerializer(serializers.ModelSerializer):
    username_validator = RegexValidator(
        r"^[\w.@+-]+\Z",
        message="Никнейм содержит недопустимы символы!",
    )
    username = serializers.CharField(
        min_length=4,
        max_length=150,
        validators=[
            username_validator,
            UniqueValidator(queryset=User.objects.all()),
        ],
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username",
                  "bio", "email", "role")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
