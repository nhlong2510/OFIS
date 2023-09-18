import django_filters
from . models import OfisInfo


class OfisFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='EinvoiceInfo__EinvoiceStatus' ,lookup_expr='icontains')
    fdate = django_filters.DateFilter(field_name='FolioCreatedDate', lookup_expr='gte')
    tdate = django_filters.DateFilter(field_name='FolioCreatedDate', lookup_expr='lte')
    folio = django_filters.CharFilter(field_name='FolioNo', lookup_expr='icontains')

    class Meta:
        model = OfisInfo
        fields = ['EinvoiceInfo', 'FolioCreatedDate', 'FolioNo']
