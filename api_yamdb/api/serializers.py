from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
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
        representation = super().to_representation(instance)
        if instance.category:
            representation['category'] = instance.category.slug
        elif instance.genre:
            representation['genre'] = [genre.slug for genre in
                                       instance.genre.all()]
        return representation


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
    score = serializers.IntegerField()

    class Meta:
        fields = ('comments', 'id', 'text', 'author',
                  'pub_date', 'score')
        model = Review
        read_only_fields = ('pub_date',)

    def validate(self, data):
        title_id = self.context.get('view').kwargs.get('title_id')
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                title_id=title_id,
                    author=self.context['request'].user).exists():
                raise serializers.ValidationError(
                    'Пользователь уже оставил отзыв на это произведение.'
                )

        if not 1 <= data['score'] <= 10:
            raise serializers.ValidationError(
                {'score': ['Оценка должна быть от 1 до 10.']}
            )

        return data
