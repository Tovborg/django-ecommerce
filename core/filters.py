import django_filters
from core.models import *


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Item
        fields = ['price', 'release_date']
