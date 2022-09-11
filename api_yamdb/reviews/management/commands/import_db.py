import csv

from django.conf import settings
from django.core.management import BaseCommand
from django.db import connection

from reviews.models import Category, Comment, Genre, Review, Title, User


MODELS = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}

TABLES = {
    'reviews_title_genre': 'genre_title.csv',
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model, csv_name in MODELS.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{csv_name}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(
                    model(**data) for data in reader)
        for table, csv_name in TABLES.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{csv_name}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                to_db = [(
                    data['id'],
                    data['title_id'],
                    data['genre_id']
                ) for data in reader]
                cursor = connection.cursor()
                cursor.executemany(
                    f'INSERT INTO {table} VALUES(?, ?, ?)',
                    to_db
                )
                connection.commit()
                cursor.close
        self.stdout.write(self.style.SUCCESS('Все данные успешно загружены!'))
