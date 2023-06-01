from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import FilterTitle
from .permissions import (
    AdminReadOnly, AdminOnly,
    AuthorModeratorAdminOrReadOnly
)
from .serializers import (
    CategorySerializer, CommentSerializer,
    GenreSerializer, UserCreateSerializer,
    ReviewSerializer, TitleEditSerializer,
    TitlesReadOnlySerializer, TokenSerializer,
    UserSerializer, BaseUserSerializer,
)


@api_view(['POST'])
def create_user(request):
    """Функция регистрации user, генерации и отправки кода на почту"""

    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')

    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )

    if not created:
        if user.username == username and user.email == email:
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.username == username:
            return Response(
                {'error': 'Username уже занят.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif user.email == email:
            return Response(
                {'error': 'Email уже зарегистрирован.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация в проекте YaMDb.',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data['username']
    )
    if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
    ):
        token = RefreshToken.for_user(user)
        return Response(
            {'access': str(token.access_token)}, status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path=settings.FORBIDDEN_USERNAME,
        permission_classes=[IsAuthenticated],
        serializer_class=BaseUserSerializer,
    )
    def get_edit_user(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )

    def get_queryset(self):
        return self.get_review().comments.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorModeratorAdminOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def get_queryset(self):
        return self.get_title().reviews.all()


class GenreCategoryMixinsBaseClass(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (AdminReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(GenreCategoryMixinsBaseClass):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewsSet(GenreCategoryMixinsBaseClass):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (AdminReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitle
    ordering = ['-rating']

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return TitlesReadOnlySerializer
        return TitleEditSerializer
