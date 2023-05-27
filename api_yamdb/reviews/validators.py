from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    now = timezone.now().year
    if value > now:
        raise ValidationError(
            (f'Сейчас идёт {now} год, а год {value} это что-то из будущего'),
            params={'value': value},
        )
    return value
