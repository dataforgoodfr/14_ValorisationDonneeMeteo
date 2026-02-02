"""
Django-filter definitions for weather API filtering.
"""

import django_filters

from .models import HoraireTempsReel, Quotidienne, Station


class StationFilter(django_filters.FilterSet):
    """Filter for weather stations."""

    code = django_filters.CharFilter()
    departement = django_filters.NumberFilter()
    poste_ouvert = django_filters.BooleanFilter()
    poste_public = django_filters.BooleanFilter()

    # Bounding box filters for geographic queries
    lat_min = django_filters.NumberFilter(field_name="lat", lookup_expr="gte")
    lat_max = django_filters.NumberFilter(field_name="lat", lookup_expr="lte")
    lon_min = django_filters.NumberFilter(field_name="lon", lookup_expr="gte")
    lon_max = django_filters.NumberFilter(field_name="lon", lookup_expr="lte")

    class Meta:
        model = Station
        fields = ["code", "departement", "frequence", "poste_ouvert", "poste_public"]


class HoraireTempsReelFilter(django_filters.FilterSet):
    """Filter for hourly real-time measurements."""

    station = django_filters.NumberFilter()
    station_code = django_filters.CharFilter(field_name="station__code")
    validity_time_after = django_filters.DateTimeFilter(
        field_name="validity_time", lookup_expr="gte"
    )
    validity_time_before = django_filters.DateTimeFilter(
        field_name="validity_time", lookup_expr="lte"
    )

    # Temperature range filters
    t_min = django_filters.NumberFilter(field_name="t", lookup_expr="gte")
    t_max = django_filters.NumberFilter(field_name="t", lookup_expr="lte")

    class Meta:
        model = HoraireTempsReel
        fields = ["station", "station_code"]


class QuotidienneFilter(django_filters.FilterSet):
    """Filter for daily aggregated data."""

    station = django_filters.NumberFilter()
    station_code = django_filters.CharFilter(field_name="station__code")
    date_after = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_before = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    # Temperature range filters
    tn_min = django_filters.NumberFilter(field_name="tn", lookup_expr="gte")
    tx_max = django_filters.NumberFilter(field_name="tx", lookup_expr="lte")

    class Meta:
        model = Quotidienne
        fields = ["station", "station_code"]
