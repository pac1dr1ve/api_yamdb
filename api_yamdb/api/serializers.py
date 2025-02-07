from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.constants import MIN_VALUE_FOR_SCORE, MAX_VALUE_FOR_SCORE


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializerForReader(serializers.ModelSerializer):
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
        return TitleSerializerForReader(instance).data


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
