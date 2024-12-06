import csv

from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, GenreTitle, Title, Review
from users.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_arguments('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file in options['csv_file']:
            reader = csv.DictReader(
                open(
                    csv_file, newline='', encoding='utf-8'
                )
            )
            for row in reader:
                if 'category.csv' in csv_file:
                    Category.objects.create(
                        id=row['id'], name=row['name'], slug=row['slug']
                    )
                if 'comments.csv' in csv_file:
                    Comment.objects.create(
                        id=row['id'],
                        review_id=row['review_id'],
                        text=row['text'],
                        author=row['author'],
                        pub_date=row['pub_date']
                    )
                if 'genre_title.csv' in csv_file:
                    GenreTitle.objects.create(
                        id=row['id'],
                        title_id=row['title_id'],
                        genre_id=row['genre_id']
                    )
                if 'genre.csv' in csv_file:
                    Genre.objects.create(
                        id=row['id'],
                        name=row['name'],
                        slug=row['slug']
                    )
                if 'review.csv' in csv_file:
                    Review.objects.create(
                        id=row['id'],
                        title_id=row['title_id'],
                        text=row['text'],
                        author=row['author'],
                        score=row['score'],
                        pub_date=row['pub_date']
                    )
                if 'title.csv' in csv_file:
                    Title.objects.create(
                        id=row['id'],
                        name=row['name'],
                        year=row['year'],
                        category=row['category']
                    )
                if 'users.csv' in csv_file:
                    User.objects.create(
                        id=row['id'],
                        username=row['username'],
                        email=row['email'],
                        role=row['role'],
                        bio=row['bio'],
                        first_name=row['first_name'],
                        last_name=row['last_name']
                    )
