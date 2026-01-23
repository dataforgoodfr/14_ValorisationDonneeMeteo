"""
DRF ViewSets for weather data API endpoints.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import HoraireTempsReelFilter, QuotidienneFilter, StationFilter
from .models import HoraireTempsReel, Quotidienne, Station
from .serializers import (
    HoraireTempsReelDetailSerializer,
    HoraireTempsReelSerializer,
    QuotidienneDetailSerializer,
    QuotidienneSerializer,
    StationDetailSerializer,
    StationSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Liste des stations",
        description="Retourne la liste des stations meteorologiques.",
        tags=["Stations"],
    ),
    retrieve=extend_schema(
        summary="Detail d'une station",
        description="Retourne les details d'une station specifique.",
        tags=["Stations"],
    ),
)
class StationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for weather station metadata.
    Provides list and retrieve actions only (read-only).
    """

    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filterset_class = StationFilter
    search_fields = ["nom", "id"]
    ordering_fields = ["nom", "departement", "alt"]
    ordering = ["nom"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StationDetailSerializer
        return StationSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Donnees horaires temps reel",
        description="Retourne les mesures horaires en temps reel.",
        tags=["Temps Reel"],
    ),
    retrieve=extend_schema(
        summary="Detail mesure horaire",
        tags=["Temps Reel"],
    ),
)
class HoraireTempsReelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for hourly real-time weather measurements.
    Optimized for time-series queries on TimescaleDB hypertable.
    """

    queryset = HoraireTempsReel.objects.all()
    serializer_class = HoraireTempsReelSerializer
    filterset_class = HoraireTempsReelFilter
    ordering_fields = ["validity_time", "t", "rr1"]
    ordering = ["-validity_time"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return HoraireTempsReelDetailSerializer
        return HoraireTempsReelSerializer

    @extend_schema(
        summary="Derniere mesure par station",
        description="Retourne la derniere mesure pour chaque station.",
        tags=["Temps Reel"],
    )
    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Get the most recent measurement for each station."""
        latest_data = HoraireTempsReel.objects.order_by(
            "geo_id_insee", "-validity_time"
        ).distinct("geo_id_insee")
        serializer = self.get_serializer(latest_data, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Donnees quotidiennes",
        description="Retourne les donnees meteorologiques journalieres agregees.",
        tags=["Quotidien"],
    ),
    retrieve=extend_schema(
        summary="Detail donnee quotidienne",
        tags=["Quotidien"],
    ),
)
class QuotidienneViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for daily aggregated weather data.
    """

    queryset = Quotidienne.objects.all()
    serializer_class = QuotidienneSerializer
    filterset_class = QuotidienneFilter
    ordering_fields = ["date", "tn", "tx", "rr"]
    ordering = ["-date"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return QuotidienneDetailSerializer
        return QuotidienneSerializer
