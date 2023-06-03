import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            (f'Указанный год {value} больше текущего {now}')
        )
    return value


def validate_username(username):
    pattern = r'^[\w.@+-]+'
    if not re.fullmatch(pattern, username):
        invalid_chars = ''.join(set(re.findall(pattern, username)))
        raise ValidationError(
            f'Некорректные символы в username: {invalid_chars}'
        )
    if username == settings.FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Ник "{settings.FORBIDDEN_USERNAME}" нельзя регистрировать!'
        )
    return username
