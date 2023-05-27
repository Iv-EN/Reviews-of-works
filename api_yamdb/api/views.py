from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from .filters import FilterTitle
from django.db.models import Avg
from .mixins import MixinsListCreateDestroyViewsSet
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleEditSerializer, TitlesReadOnlySerializer)

from reviews.models import Category, Genre, Review, Title
from users.permissions import (ListOrAdminModeratOnly,
                               AuthenticatedPrivilegedUsersOrReadOnly)


def redoc(request):
    return render(request, 'api/redoc.html')


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AuthenticatedPrivilegedUsersOrReadOnly]

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return review.comments.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [AuthenticatedPrivilegedUsersOrReadOnly]

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)

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
