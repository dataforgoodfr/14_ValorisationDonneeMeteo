"""
Django-filter definitions for weather API filtering.
"""

import django_filters

from .models import Station


class StationFilter(django_filters.FilterSet):
    """Filter for weather stations (read-only view)."""

    # Compat API: on garde le paramètre "code" mais il filtre station_code
    code = django_filters.CharFilter(field_name="station_code")
    departement = django_filters.NumberFilter(field_name="departement")

    # Compat API: mêmes noms qu'avant
    poste_ouvert = django_filters.BooleanFilter(field_name="is_open")
    poste_public = django_filters.BooleanFilter(field_name="is_public")

    # Bounding box filters for geographic queries
    lat_min = django_filters.NumberFilter(field_name="lat", lookup_expr="gte")
    lat_max = django_filters.NumberFilter(field_name="lat", lookup_expr="lte")
    lon_min = django_filters.NumberFilter(field_name="lon", lookup_expr="gte")
    lon_max = django_filters.NumberFilter(field_name="lon", lookup_expr="lte")

    class Meta:
        model = Station
        fields = [
            "code",
            "departement",
            "poste_ouvert",
            "poste_public",
        ]
