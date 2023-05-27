from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404

from .filters import FilterTitle
from .mixins import ModelMixinSet
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleEditSerializer,
    TitlesReadOnlySerializer
)
from reviews.models import Category, Genre, Review, Title
from users.permissions import (
    ListOrAdminModeratOnly,
    AuthenticatedPrivilegedUsersOrReadOnly
)


def redoc(request):
    return render(request, 'api/redoc.html')


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthenticatedPrivilegedUsersOrReadOnly,)

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, pk=review_id)

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
    permission_classes = (AuthenticatedPrivilegedUsersOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def get_queryset(self):
        return self.get_title().reviews.all()


class GenreCategoryViewSetBaseClass(ModelMixinSet):
    permission_classes = (ListOrAdminModeratOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(GenreCategoryViewSetBaseClass):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewsSet(GenreCategoryViewSetBaseClass):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')).order_by('id')
    serializer_class = TitlesReadOnlySerializer
    permission_classes = (ListOrAdminModeratOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitle

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return TitlesReadOnlySerializer
        return TitleEditSerializer
