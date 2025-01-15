import os
import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, GenreTitle, Title, Review
from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')

        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(
                f'Папка с данными не найдена: {data_dir}'))
            return

        file_to_model = {
            'users.csv': User,
            'category.csv': Category,
            'genre.csv': Genre,
            'titles.csv': Title,
            'genre_title.csv': GenreTitle,
            'review.csv': Review,
            'comments.csv': Comment,
        }

        for file, model in file_to_model.items():
            file_path = os.path.join(data_dir, file)
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(
                    f'Файл {file} не найден, продолжаем'))
                continue
            self.stdout.write(self.style.SUCCESS(f'Файл {file} загружен.'))

            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                objects = []

                for row in reader:
                    objects.extend(self.create_objects(model, row))

                model.objects.bulk_create(objects)
                self.stdout.write(self.style.SUCCESS(
                    f'Данные из {file} успешно загружены.'))

        self.stdout.write(self.style.SUCCESS(
            'Загрузка данных завершена успешно.'))

    def create_objects(self, model, row):
        objects = []
        if model == User and not User.objects.filter(id=row['id']).exists():
            objects.append(User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                role=row['role'],
                bio=row['bio'],
                first_name=row['first_name'],
                last_name=row['last_name']
            ))
        if model == Category and not Category.objects.filter(
                id=row['id']).exists():
            objects.append(Category(
                id=row['id'],
                name=row['name'],
                slug=row['slug']
            ))
        if model == Genre and not Genre.objects.filter(id=row['id']).exists():
            objects.append(Genre(
                id=row['id'],
                name=row['name'],
                slug=row['slug']
            ))
        if model == Title and not Title.objects.filter(id=row['id']).exists():
            objects.append(Title(
                id=row['id'],
                name=row['name'],
                year=row['year'],
                category=Category.objects.get(id=row['category'])
            ))
        if model == GenreTitle and not GenreTitle.objects.filter(
                id=row['id']).exists():
            objects.append(GenreTitle(
                id=row['id'],
                title_id=row['title_id'],
                genre_id=row['genre_id']
            ))
        if model == Review and not Review.objects.filter(
                id=row['id']).exists():
            objects.append(Review(
                id=row['id'],
                title_id=row['title_id'],
                text=row['text'],
                author=User.objects.get(id=row['author']),
                score=row['score'],
                pub_date=datetime.strptime(row['pub_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            ))
        if model == Comment and not Comment.objects.filter(
                id=row['id']).exists():
            objects.append(Comment(
                id=row['id'],
                review_id=row['review_id'],
                text=row['text'],
                author=User.objects.get(id=row['author']),
                pub_date=row['pub_date']
            ))
        return objects
