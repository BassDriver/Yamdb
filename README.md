![yamdb_workflow](https://github.com/BassDriver/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

Проект для проверки доступен по адресу: [http://51.250.79.153/](http://51.250.79.153/)

# API YaMDb
### Описание проекта API YaMDB:

Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором.

Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

## Системные требования/технологии:

- Python 3.7
- Django
- DRF
- Simple-JWT
- PostgreSQL
- Docker
- nginx
- gunicorn

## Запуск проекта в контейнерах:
Сначала нужно клонировать репозиторий и перейти в корневую папку:
```
git clone git@github.com:BassDriver/yamdb_final.git
cd yamdb_final
```
Затем нужно перейти в папку yamdb_final/infra и создать в ней файл .env с переменными окружения, необходимыми для работы приложения.
```
cd infra/
```
Пример содержимого файла env:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=key
```
Далее следует запустить docker-compose:
```
docker-compose up -d
```
Будут созданы и запущены в фоновом режиме необходимые для работы приложения контейнеры (db, web, nginx).

Затем нужно внутри контейнера web выполнить миграции, создать суперпользователя и собрать статику:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
После этого проект должен быть доступен по адресу [http://localhost/](http://localhost/).

### Заполнение базы данных:
Нужно зайти на на  [http://localhost/admin/](http://localhost/admin/), авторизоваться и внести записи в базу данных через админку.

Резервную копию базы данных можно создать командой:
```
docker-compose exec web python manage.py dumpdata > fixtures.json
```
Загрузка базы данных осуществляется командой:
```
docker-compose exec web python manage.py loaddata fixtures.json
```
## Полная документация API

по адресу http://localhost/redoc/

Пример запроса: 
- Получение подписок пользователя (username указывается в теле запроса):
```
GET http://127.0.0.1:8000/api/v1/follow/
```
Пример ответа в случае успешного запроса:
```
[
    {
        "user": "string",
        "following": "string"
    }
]
```
## Команда разработки

- :white_check_mark: [Анна Иванова (в роли Python-разработчика, Тимлид)](https://github.com/19n9)

- :white_check_mark: [Михаил Гусев (в роли Python-разработчика)](https://github.com/Gra4-5051)

- :white_check_mark: [Сергей Шубин (в роли Python-разработчика)](https://github.com/BassDriver)
