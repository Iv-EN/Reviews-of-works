from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator, MinValueValidator,
)
from django.db import models

from reviews.validators import validate_year, validate_username


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
    username = models.CharField(
        max_length=settings.LEN_USERNAME_NAME,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[validate_username]
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
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        blank=True
    )
    email = models.EmailField(max_length=settings.LEN_EMAIL, unique=True)
    bio = models.TextField(
        verbose_name='О себе',
        blank=True
    )

    @property
    def is_admin(self):
        return (
            self.role == ADMIN or self.is_staff
        )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_moderator(self):
        return self.role == MODERATOR


class GenreCategoryBaseClass(models.Model):
    name = models.CharField(
        max_length=256,
        db_index=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Путь (имя каталога)',
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:30]


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
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория',
        related_name='titles'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:30]


class TextAuthorPubDate(models.Model):
    pub_date = models.DateTimeField(
        verbose_name='Время добавления',
        auto_now_add=True,
        null=True
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='%(class)ss'
    )

    def __str__(self):
        return f'{self.author.username}: {self.text[:15]}'

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        default_related_name = '%(class)ss'


class Review(TextAuthorPubDate):
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

    class Meta(TextAuthorPubDate.Meta):
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревью'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(TextAuthorPubDate):
    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        verbose_name='Ревью'
    )

    class Meta(TextAuthorPubDate.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
