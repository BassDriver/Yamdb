import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.')
        )
    reg = re.sub(r'[\w.@+-]', '', value)
    if reg:
        raise ValidationError(
            f'Username должен содержать только буквы, '
            f'цифры и символы:"@", ".", "+", "-", "_". '
            f'Введены следующие недопустимые символы: {reg}'
        )
    return value


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError(
            (f'{value} год не должен быть больше нынешнего!')
        )
    return value
