from django.contrib.auth.models import AbstractUser
from django.db import models

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    """Пользователь"""

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(
        verbose_name='О себе',
        max_length=1024,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=5,
        verbose_name='Код подтверждения',
        blank=True
    )

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_moderator(self):
        return self.role == MODERATOR
