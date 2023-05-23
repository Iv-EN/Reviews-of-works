from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from reviews.models import Category, Comment, Genre, Review, Title
from users.permissions import ListOrAdminModeratOnly

from .filters import FilterTitle
from .mixins import MixinsListCreateDestroyViewsSet
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleEditSerializer, TitlesReadOnlySerializer)


def redoc(request):
    return render(request, 'api/redoc.html')


class CommentViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    # permission_classes = ...
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        serializer.save(author=self.request.user, review_id=review_id)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        comments_queryset = Comment.objects.filter(review=review_id)
        return comments_queryset


class ReviewViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    # permission_classes = ...
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user, title_id=title_id)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_queryset = Review.objects.filter(title=title_id)
        return review_queryset


class CategoryViewSet(MixinsListCreateDestroyViewsSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ListOrAdminModeratOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewsSet(MixinsListCreateDestroyViewsSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ListOrAdminModeratOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (ListOrAdminModeratOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitle

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleEditSerializer
        return TitlesReadOnlySerializer
