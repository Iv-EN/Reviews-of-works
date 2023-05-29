from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api_yamdb.settings import USERNAME_NAME, EMAIL
from reviews.models import Category, Comment, Genre, Review, Title
from users.validators import ValidateUsername

User = get_user_model()


class UserCreateSerializer(serializers.Serializer, ValidateUsername):
    class Meta:
        model = User
        fields = ('username', 'email')


class BaseUserSerializer(serializers.ModelSerializer, ValidateUsername):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        read_only_fields = ('role',)


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        read_only_fields = ()

    def validate_role(self, role):
        req_user = self.context['request'].user
        user = User.objects.get(username=req_user)

        if user.is_moderator:
            if role != 'admin':
                role = 'admin'
        elif user.is_user:
            role = user.role
        return role


class RegistrationSerializer(serializers.Serializer, ValidateUsername):
    username = serializers.CharField(required=True, max_length=USERNAME_NAME)
    email = serializers.EmailField(required=True, max_length=EMAIL)


class TokenSerializer(serializers.Serializer, ValidateUsername):
    username = serializers.CharField(required=True, max_length=USERNAME_NAME)
    confirmation_code = serializers.CharField(required=True)


class UserEditSerializer(UserSerializer):
    """Сериализатор модели User для get и patch"""

    role = serializers.CharField(read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = (
            'id', 'text', 'author', 'pub_date')
        model = Comment


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    def validate(self, data):
        request = self.context['request']
        if request.method == 'POST':
            title = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(title=title,
                                     author=request.user).exists():
                raise ValidationError('Вы не можете добавить более'
                                      'одного отзыва на произведение')
        return data

    class Meta:
        model = Review
        exclude = ('title',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitlesReadOnlySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    description = serializers.CharField(read_only=True)
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'rating', 'genre', 'category')


class TitleEditSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category')
