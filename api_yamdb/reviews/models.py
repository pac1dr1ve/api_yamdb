from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .constants import (
    LENGTH_FOR_NAME,
    LENGTH_FOR_SLUG,
    CLIPPING_LENGTH,
    MIN_VALUE_FOR_SCORE,
    MAX_VALUE_FOR_SCORE
)

User = get_user_model()


class NameAndSlugAbstractModel(models.Model):
    name = models.CharField(
        max_length=LENGTH_FOR_NAME,
        verbose_name='Категория'
    )
    slug = models.SlugField(
        max_length=LENGTH_FOR_SLUG,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        abstract = True
        ordering = ('name', )
        verbose_name = 'Базовая модель для категории и жанра'
        verbose_name_plural = 'Базовые модели для категорий и жанров'

    def __str__(self):
        return self.name[:CLIPPING_LENGTH]


class TextAndAuthorAndPubDateAbstractModel(models.Model):
    text = models.TextField(
        verbose_name='Текст'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True
    )

    class Meta:
        abstract = True
        verbose_name = 'Базовая модель для комментария и отзыва'
        verbose_name_plural = 'Базовые модели для комментарий и отзывов'

    def __str__(self):
        return self.text[:CLIPPING_LENGTH]


class Category(NameAndSlugAbstractModel):
    class Meta(NameAndSlugAbstractModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameAndSlugAbstractModel):
    class Meta(NameAndSlugAbstractModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


def current_year():
    return datetime.now().year


class Title(models.Model):
    name = models.CharField(
        max_length=LENGTH_FOR_NAME,
        verbose_name='Произведение'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска',
        validators=(
            MaxValueValidator(
                limit_value=current_year,
                message='Год выпуска не может быть больше текущего года!'),
        )
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:CLIPPING_LENGTH]


class Review(TextAndAuthorAndPubDateAbstractModel):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка произведения',
        validators=(
            MinValueValidator(
                limit_value=MIN_VALUE_FOR_SCORE,
                message=f'Минимальная оценка: {MIN_VALUE_FOR_SCORE} балл'
            ),
            MaxValueValidator(
                limit_value=MAX_VALUE_FOR_SCORE,
                message=f'Максимальная оценка: {MAX_VALUE_FOR_SCORE} баллов'
            )
        )
    )

    class Meta(TextAndAuthorAndPubDateAbstractModel.Meta):
        unique_together = ('author', 'title')
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(TextAndAuthorAndPubDateAbstractModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta(TextAndAuthorAndPubDateAbstractModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
