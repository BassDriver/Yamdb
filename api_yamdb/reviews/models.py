import api_yamdb.settings as settings

from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator)
from django.db import models

from .validators import validate_year, validate_username


USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.CharField(max_length=settings.USERNAME_MAX_LENGTH,
                                unique=True,
                                blank=False,
                                null=False,
                                validators=[validate_username],
                                )
    email = models.EmailField(unique=True,
                              max_length=settings.EMAIL_MAX_LENGTH,
                              blank=False,
                              null=False
                              )
    role = models.CharField(
        max_length=max(len(role[1]) for role in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=settings.CONFIRMATION_CODE_MAX_LENGTH,
        null=True,
        default=settings.CONFIRMATION_CODE_DEFAULT,
        blank=False,
    )

    first_name = models.CharField(
        max_length=settings.FIRST_NAME_MAX_LENGTH, blank=True)
    last_name = models.CharField(
        max_length=settings.LAST_NAME_MAX_LENGTH, blank=True)
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='О себе'
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username


class GenreCategory(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Идентификатор',
        unique=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name[:15]


class Genre(GenreCategory):

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)


class Category(GenreCategory):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.TextField(
        verbose_name='Название произведения',
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        db_index=True,
        null=True,
        verbose_name='Год произведения',
        validators=[validate_year],
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        related_name='titles',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        verbose_name='Категория',
        db_index=True,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class CreatedModel(models.Model):
    text = models.TextField(
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='%(class)s'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(CreatedModel):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Рейтинг',
        validators=[
            MinValueValidator(1, 'Допустимы значения от 1 до 10'),
            MaxValueValidator(10, 'Допустимы значения от 1 до 10')
        ]
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique'
            ),
        ]


class Comment(CreatedModel):
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
