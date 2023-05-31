from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator, MinValueValidator,
    RegexValidator
)
from django.db import models

from reviews.validators import validate_year
from api_yamdb.settings import USERNAME_NAME, EMAIL


USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)

MAX_LENGTH = max(len(choice[0]) for choice in ROLE_CHOICES)


def username_validator():
    """Функция для создания валидатора username."""

    return RegexValidator(
        regex=r'^[\w.@+-]+$',
        message='Username может содержать только буквы,'
                'цифры и символы @/./+/-/_.'
    )


class User(AbstractUser):
    """Пользователь"""
    username = models.CharField(
        max_length=USERNAME_NAME,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[username_validator()]
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True
    )

    role = models.CharField(
        max_length=MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    email = models.EmailField(max_length=EMAIL, unique=True)
    bio = models.TextField(
        verbose_name='О себе',
        max_length=150,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=5,
        verbose_name='Код подтверждения',
        blank=True
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or User.objects.filter(
            is_staff=True,
            is_superuser=True
        ).exists()

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_moderator(self):
        return self.role == MODERATOR


class GenreCategoryBaseClass(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Адрес',
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)


class Category(GenreCategoryBaseClass):

    class Meta(GenreCategoryBaseClass.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(GenreCategoryBaseClass):

    class Meta(GenreCategoryBaseClass.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год выпуска',
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class CommonClass(models.Model):
    pub_date = models.DateTimeField(
        verbose_name='Время добавления',
        auto_now_add=True,
        null=True
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='%(class)s'
    )

    def __str__(self):
        return f'{self.author.username}: {self.text[:15]}'

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class Review(CommonClass):
    title = models.ForeignKey(
        to=Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.SmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
        verbose_name='Оценка',
    )

    class Meta:
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревью'
        default_related_name = 'reviews'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(CommonClass):
    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        verbose_name='Ревью'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('-pub_date',)
