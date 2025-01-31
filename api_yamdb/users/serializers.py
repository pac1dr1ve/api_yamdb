from django.core.validators import RegexValidator
from rest_framework import serializers

from reviews.constants import MAX_NAMES_STRINGS, MAX_EMAIL_STRING
from users.common import UserService
from users.mixin import UsernameValidationMixin
from users.models import User


class UserTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=5)

    def validate(self, data):
        user = User.objects.get(username=data.get("username"))
        if user.confirmation_code != data.get("confirmation_code"):
            raise serializers.ValidationError("Неверный код подтверждения")
        return data


class SignUpSerializer(serializers.Serializer, UsernameValidationMixin):
    email = serializers.EmailField(
        max_length=MAX_EMAIL_STRING, required=True
    )
    username_validator = RegexValidator(
        r"^[\w.@+_-]+\Z",
        message=(
            "Можно использовать только буквы (включая буквы в верхнем и "
            "нижнем регистрах), цифры и спецсимволы: ., @, +, -"
        )
    )
    username = serializers.CharField(max_length=MAX_NAMES_STRINGS,
                                     validators=[username_validator])

    def validate(self, data):
        email = data.get("email")
        username = data.get("username")

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if user_by_email and user_by_username:
            if user_by_email == user_by_username:
                return data
            raise serializers.ValidationError({
                "email": "Email уже занят.",
                "username": "Username уже занят."
            })

        if user_by_email:
            raise serializers.ValidationError({"email": "Email уже занят."})

        if user_by_username:
            raise serializers.ValidationError(
                {"username": "Username уже занят."}
            )

        return data

    def create(self, validated_data):
        email = validated_data["email"]
        username = validated_data["username"]

        existing_user_email = User.objects.filter(email=email).first()
        existing_user_username = User.objects.filter(username=username).first()

        confirmation_code = UserService.create_confirmation_code()

        if existing_user_email and existing_user_username:
            existing_user_email.confirmation_code = confirmation_code
            existing_user_email.save()
            UserService.send_confirmation_email(
                existing_user_email, confirmation_code
            )
            return validated_data

        if existing_user_email:
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )

        if existing_user_username:
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует."
            )

        user = User(**validated_data)
        user.password = "qwerty"  # TODO: Заменить на генерацию пароля
        user.confirmation_code = confirmation_code
        user.full_clean()
        user.save()

        UserService.send_confirmation_email(user, confirmation_code)

        return validated_data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "username", "bio", "email", "role"
        )

    def update(self, instance, validated_data):
        new_role = validated_data.get("role")
        if (new_role and new_role != instance.role
                and self.context["request"].user.role == "admin"):
            instance.role = new_role
        if "role" in validated_data:
            del validated_data["role"]
        return super().update(instance, validated_data)
