# comerciantes/filters.py
import django_filters
from django.db.models import Q 
from .models import Business, Offer

# --- Filtro para el modelo Business ---
class BusinessFilter(django_filters.FilterSet):
    """
    Filtro personalizado para el modelo Business.
    Permite filtrar por una búsqueda de texto en múltiples campos,
    tipo de negocio y por municipio.
    """
    search = django_filters.CharFilter(method='filter_search')
    business_type = django_filters.CharFilter(field_name='business_type', lookup_expr='iexact') 
    municipality = django_filters.CharFilter(field_name='municipality', lookup_expr='iexact')

    class Meta:
        model = Business
        fields = []
    
    def filter_search(self, queryset, name, value):
        # Implementa la lógica de búsqueda de texto "OR" en varios campos
        # Busca en el nombre del negocio, qué venden, municipio y tipo de negocio
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(what_they_sell__icontains=value) | 
            Q(municipality__icontains=value) |
            Q(business_type__icontains=value)
        )


# --- Filtro para el modelo Offer (el que ya tenías) ---
class OfferFilter(django_filters.FilterSet):
    """
    Filtro para el modelo Offer.
    Permite filtrar por búsqueda de texto, tipo de negocio y municipio.
    """
    search = django_filters.CharFilter(method='filter_search')
    business_type = django_filters.CharFilter(field_name='business__business_type', lookup_expr='iexact') 
    municipality = django_filters.CharFilter(field_name='business__municipality', lookup_expr='iexact')

    class Meta:
        model = Offer
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | 
            Q(description__icontains=value) | 
            Q(business__name__icontains=value)
        )
