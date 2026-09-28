import django_filters
from .models import Lead

class LeadFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Lead.StatusChoices.choices)
    source = django_filters.CharFilter(lookup_expr='iexact')
    source_contains = django_filters.CharFilter(field_name='source', lookup_expr='icontains')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to__id')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Lead
        fields = ['status', 'source', 'assigned_to']
