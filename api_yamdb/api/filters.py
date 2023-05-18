import django_filters as filters

from .models import Title


class FilterTitle(filters.FilterSet):
    genre = filters.CharFilter(field_name='slug_genre')
    category = filters.CharFilter(field_name='slug_category')
    year = filters.NumberFilter(field_name='year')
    name = filters.CharFilter(field_name='name', lookup_expr='contains')

    class Meta:
        model = Title
        fields = '__all__'
