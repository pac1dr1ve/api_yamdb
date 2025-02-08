# Generated by Django 3.2.25 on 2025-02-08 12:19

import django.core.validators
from django.db import migrations, models
import reviews.models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0011_auto_20250126_1531'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('name',), 'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ('name',), 'verbose_name': 'Жанр', 'verbose_name_plural': 'Жанры'},
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(limit_value=reviews.models.current_year, message='Год выпуска не может быть больше текущего года!')], verbose_name='Год выпуска'),
        ),
    ]
