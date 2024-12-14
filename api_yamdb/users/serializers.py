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
    email = serializers.EmailField(
        max_length=254,
    )
    username = serializers.CharField(
        min_length=4,
        max_length=150,
    )
    first_name = serializers.CharField(
        min_length=4,
        max_length=150,
        required=False,
    )
    last_name = serializers.CharField(
        required=False,
        min_length=4,
        max_length=150,
    )
    bio = serializers.CharField(
        required=False
    )
    # TODO использовать enum.role
    role = serializers.CharField(
        required=False
    )

    # TODO Рефакторинг - last_name проверяем на уровне полей, а не валидациu
    # def validate_last_name(self, value):
    #     if len(value) < 4 or len(value) > 150:
    #         raise serializers.ValidationError("Фамилия должна быть от 4 до 150 символов")
    #     return value

    def validate_username(self, value: str) -> str:
        if value.lower() == "me":
            raise serializers.ValidationError("Недопустимое имя пользователя")
        if not re.fullmatch(r"^[\w.@+-]+\Z", value):
            raise serializers.ValidationError("Никнейм содержит недопустимы символы!")
        # if 4 < len(value) > 150:
        #     raise serializers.ValidationError(
        #         "Количество символов в никнейме должно быть от 4 до 150",
        #     )
        return value

    # TODO Рефакторинг - email проверяем на уровне полей, а не валидациu
    def validate_email(self, value):
        if 6 < len(value) > 256:
            raise serializers.ValidationError(
                "Количество символов названия почты должно быть от 6 до 256",
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "bio", "email", "role")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
