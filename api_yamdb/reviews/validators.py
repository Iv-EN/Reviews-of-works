import re
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            (f'Указанный год {value} больше текущего {now}')
        )
    return value


class ValidateUsernameMixin:
    """Валидаторы для username."""

    def validate_username(self, username):
        pattern = r'^[\w.@+-]+'
        if not re.fullmatch(pattern, username):
            raise ValidationError(
                f'Некорректные символы в username: {username}'
            )
        if username == settings.FORBIDDEN_USERNAME:
            raise ValidationError(
                f'Ник "{settings.FORBIDDEN_USERNAME}" нельзя регистрировать!'
            )
        return username
