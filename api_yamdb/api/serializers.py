from django.db import models
from django.shortcuts import get_object_or_404
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from users.common import UserService
from users.mixin import UsernameValidationMixin
from users.models import User
from reviews.models import Category, Comment, Genre, Review, Title
from reviews.constants import (
    MIN_VALUE_FOR_SCORE,
    MAX_VALUE_FOR_SCORE,
    MAX_NAMES_STRINGS,
    MAX_CONFORMATION_CODE_STRING,
    MAX_EMAIL_STRING
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadOnlySerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True, default=None)
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ('reviews', 'id', 'name', 'year', 'description',
                  'category', 'genre', 'rating')


class TitleSerializerForWrite(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = ('reviews', 'id', 'name', 'year',
                  'description', 'category', 'genre')

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Список жанров не может быть пустым!')
        return value

    def to_representation(self, instance):
        return TitleReadOnlySerializer(instance).data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('pub_date',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    score = serializers.IntegerField(
        validators=(
            MinValueValidator(
                MIN_VALUE_FOR_SCORE,
                message=(f'Оценка должна быть от {MIN_VALUE_FOR_SCORE}'
                         f'до {MAX_VALUE_FOR_SCORE}.')),
            MaxValueValidator(
                MAX_VALUE_FOR_SCORE,
                message=(f'Оценка должна быть от {MIN_VALUE_FOR_SCORE}'
                         f'до {MAX_VALUE_FOR_SCORE}.')),
        )
    )

    class Meta:
        fields = ('comments', 'id', 'text', 'author',
                  'pub_date', 'score')
        model = Review
        read_only_fields = ('pub_date',)

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(title_id=title_id,
                                     author=request.user).exists():
                raise serializers.ValidationError(
                    'Пользователь уже оставил отзыв на это произведение.'
                )

        return data


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
