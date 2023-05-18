from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .filters import FilterTitle
from .mixins import MixinsListCreateDestroyViewsSet
from .models import Category, Genre, Title
from .permissions import IsAdminOrReadOnly
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleEditSerializer, TitlesReadOnlySerializer)


def redoc(request):
    return render(request, 'api/redoc.html')


class CategoryViewSet(MixinsListCreateDestroyViewsSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewsSet(MixinsListCreateDestroyViewsSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitle

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitleEditSerializer
        return TitlesReadOnlySerializer
