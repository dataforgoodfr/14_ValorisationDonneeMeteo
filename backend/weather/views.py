"""
DRF ViewSets for weather data API endpoints.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.bootstrap_itn import ITNDependencyProvider
from weather.services.national_indicator.use_case import get_national_indicator

from .filters import StationFilter
from .models import Station
from .serializers import (
    ErrorSerializer,
    NationalIndicatorQuerySerializer,
    NationalIndicatorResponseSerializer,
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
    search_fields = ["name", "departement", "station_code"]
    ordering_fields = ["name", "departement", "alt"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StationDetailSerializer
        return StationSerializer


class NationalIndicatorAPIView(APIView):
    """
    GET /api/v1/temperature/national-indicator
    Implémentation mock (sans BDD), conforme au contrat OpenAPI.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = NationalIndicatorQuerySerializer(data=request.query_params)
        if not q.is_valid():
            return Response(
                ErrorSerializer.build(
                    code="INVALID_PARAMETER",
                    message="Paramètre invalide ou manquant",
                    details=q.errors,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        params = q.validated_data
        ds = ITNDependencyProvider.get_dep()
        data = get_national_indicator(data_source=ds, **params)
        metadata = {
            "date_start": params["date_start"],
            "date_end": params["date_end"],
            "baseline": "1991-2020",
            "granularity": params["granularity"],
            "slice_type": params.get("slice_type", "full"),
        }

        if "month_of_year" in params:
            metadata["month_of_year"] = params["month_of_year"]

        if "day_of_month" in params:
            metadata["day_of_month"] = params["day_of_month"]

        full_payload = {
            "metadata": metadata,
            "time_series": data["time_series"],
        }
        out = NationalIndicatorResponseSerializer(data=full_payload)
        out.is_valid(raise_exception=True)

        return Response(out.data, status=status.HTTP_200_OK)
