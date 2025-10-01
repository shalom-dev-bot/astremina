import django_filters
from properties.models import Property

class PropertyFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(lookup_expr='icontains')
    neighborhood = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_bedrooms = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')
    max_bedrooms = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='lte')
    min_surface = django_filters.NumberFilter(field_name='surface_area', lookup_expr='gte')
    max_surface = django_filters.NumberFilter(field_name='surface_area', lookup_expr='lte')
    
    class Meta:
        model = Property
        fields = ['property_type', 'city', 'neighborhood']