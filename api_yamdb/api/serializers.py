from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True, default=None)
    category = CategorySerializer()
    genre = GenreSerializer()

    class Meta:
        model = Title
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('pub_date',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    score = serializers.IntegerField()
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('pub_date',)

    def validate(self, data):
        # Проверка на дублирование отзывов от одного пользователя
        # на одно произведение
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if self.context['request'].method == 'POST':
            try:
                Review.objects.get(
                    title=title,
                    author=self.context['request'].user
                )
                raise serializers.ValidationError(
                    'Пользователь уже оставил отзыв на это произведение.'
                )
            except Review.DoesNotExist:
                pass
        return data
