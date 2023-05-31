from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            (f'Указанный год {value} больше текущего {now}')
        )
    return value
