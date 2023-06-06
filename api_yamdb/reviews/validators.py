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
    PATTERN = re.compile(r'[\w.@+-]+')
    matches = PATTERN.fullmatch(username)
    invalid_chars = PATTERN.sub('', username)
    if matches is None:
        raise ValidationError(
            f'Некорректные символы в username: {invalid_chars}'
        )
    elif username == settings.FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Username "{settings.FORBIDDEN_USERNAME}" нельзя регистрировать!'
        )
    return username
