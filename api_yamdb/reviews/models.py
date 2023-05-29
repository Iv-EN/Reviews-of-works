from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import validate_year

User = get_user_model()


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
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class ReviewCommentBaseClass(models.Model):
    pub_date = models.DateTimeField(
        verbose_name='Время добавления',
        auto_now_add=True,
        null=True
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    def __str__(self):
        return f'{self.author.username}: {self.text[:15]}'

    class Meta:
        abstract = True
        ordering = ('pub_date',)


class Review(ReviewCommentBaseClass):
    title = models.ForeignKey(
        to=Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.SmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
        verbose_name='Оценка',
    )

    class Meta:
        verbose_name = 'Ревью'
        verbose_name_plural = 'Ревью'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(ReviewCommentBaseClass):
    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        verbose_name='Ревью'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
