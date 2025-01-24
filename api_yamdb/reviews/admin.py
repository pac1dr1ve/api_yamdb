from django.contrib import admin

from reviews.models import (
    Category, Genre, Title,
    Review, Comment)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = 'Не задано'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    empty_value_display = 'Не задано'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category')
    list_filter = ('year', 'genre', 'category')
    search_fields = ('name', 'description')
    filter_horizontal = ('genre',)
    empty_value_display = 'Не задано'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'score', 'pub_date')
    list_filter = ('title', 'author', 'score')
    search_fields = ('text',)
    empty_value_display = 'Не задано'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'review', 'pub_date')
    list_filter = ('author', 'review')
    search_fields = ('text',)
    empty_value_display = 'Не задано'
