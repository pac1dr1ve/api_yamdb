import os
import csv
from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand

from reviews.models import Title, Genre


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')

        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(
                f'Папка с данными не найдена: {data_dir}'))
            return

        file_to_model = {
            'users.csv': 'users.User',
            'category.csv': 'reviews.Category',
            'genre.csv': 'reviews.Genre',
            'titles.csv': 'reviews.Title',
            'review.csv': 'reviews.Review',
            'comments.csv': 'reviews.Comment',
        }

        for file, model_path in file_to_model.items():
            file_path = os.path.join(data_dir, file)
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(
                    f'Файл {file} не найден, продолжаем'))
                continue

            model = apps.get_model(model_path)
            self.stdout.write(self.style.SUCCESS(
                f'Загрузка данных из файла {file}...'))

            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                objects = []

                for row in reader:
                    if model.objects.filter(id=row['id']).exists():
                        continue

                    object_data = self.prepare_object_data(model, row)
                    objects.append(model(**object_data))

            model.objects.bulk_create(objects)
            self.stdout.write(self.style.SUCCESS(
                f'Данные из {file} успешно загружены.'))

        genre_title_file = os.path.join(data_dir, 'genre_title.csv')
        if os.path.exists(genre_title_file):
            self.load_genres(genre_title_file)
        else:
            self.stdout.write(self.style.WARNING(
                'Файл genre_title.csv не найден, пропускаем'))

        self.stdout.write(self.style.SUCCESS(
            'Загрузка данных завершена успешно.'))

    def prepare_object_data(self, model, row):
        object_data = {}

        for field, value in row.items():
            if field in ('category', 'author'):
                object_data[field] = model._meta.get_field(
                    field).related_model.objects.get(id=value)
            elif field == 'pub_date':
                object_data[field] = datetime.strptime(
                    value, '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                object_data[field] = value

        return object_data

    def load_genres(self, file_path):
        self.stdout.write(self.style.SUCCESS(
            'Обработка файла genre_title.csv...'))

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                title.genre.add(genre)

        self.stdout.write(self.style.SUCCESS('Жанры успешно добавлены.'))
