"""
DRF ViewSets for weather data API endpoints.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from weather.bootstrap_itn import ITNDependencyProvider
from weather.bootstrap_temperature_deviation import (
    TemperatureDeviationDependencyProvider,
    TemperatureDeviationOverviewDependencyProvider,
)
from weather.bootstrap_temperature_records import TemperatureRecordsDependencyProvider
from weather.services.national_indicator.use_case import get_national_indicator
from weather.services.temperature_deviation.use_case import (
    get_temperature_deviation,
    get_temperature_deviation_overview,
)
from weather.services.temperature_records.types import TemperatureRecordsRequest
from weather.services.temperature_records.use_case import get_temperature_records

from .filters import StationFilter
from .models import Station
from .serializers import (
    ErrorSerializer,
    NationalIndicatorQuerySerializer,
    NationalIndicatorResponseSerializer,
    StationDetailSerializer,
    StationSerializer,
    TemperatureDeviationGraphQuerySerializer,
    TemperatureDeviationOverviewQuerySerializer,
    TemperatureDeviationOverviewResponseSerializer,
    TemperatureDeviationResponseSerializer,
    TemperatureRecordEntrySerializer,
    TemperatureRecordsQuerySerializer,
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
        deps = ITNDependencyProvider.get_dep()
        data = get_national_indicator(
            observed_data_source=deps.observed_data_source,
            baseline_data_source=deps.baseline_data_source,
            **params,
        )
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


class TemperatureDeviationGraphAPIView(APIView):
    """
    GET /api/v1/temperature/deviation/graph
    Implémentation mock, alignée sur le pattern ITN.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = TemperatureDeviationGraphQuerySerializer(data=request.query_params)
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
        ds = TemperatureDeviationDependencyProvider.get_dep()
        try:
            data = get_temperature_deviation(data_source=ds, **params)
        except NotImplementedError as exc:
            return Response(
                ErrorSerializer.build(
                    code="NOT_IMPLEMENTED",
                    message=str(exc),
                ),
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
        full_payload = {
            "metadata": {
                "date_start": params["date_start"],
                "date_end": params["date_end"],
                "baseline": "1991-2020",
                "granularity": params["granularity"],
            },
            **data,
        }

        out = TemperatureDeviationResponseSerializer(data=full_payload)
        out.is_valid(raise_exception=True)

        return Response(out.data, status=status.HTTP_200_OK)


class TemperatureRecordsAPIView(APIView):
    """
    GET /api/v1/temperature/records
    Retourne les records absolus de température par station.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = TemperatureRecordsQuerySerializer(data=request.query_params)
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
        ds = TemperatureRecordsDependencyProvider.get_dep()

        req = TemperatureRecordsRequest(
            period_type=params["period_type"],
            type_records=params["type_records"],
            month=params.get("month"),
            season=params.get("season"),
        )

        try:
            entries = get_temperature_records(request=req, data_source=ds)
        except ValueError as exc:
            return Response(
                ErrorSerializer.build(
                    code="INVALID_PARAMETER",
                    message=str(exc),
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TemperatureRecordEntrySerializer(
            [
                {
                    "station_id": e.station_id,
                    "station_name": e.station_name,
                    "department": e.department,
                    "record_value": e.record_value,
                    "record_date": e.record_date,
                }
                for e in entries
            ],
            many=True,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class TemperatureDeviationOverviewAPIView(APIView):
    """
    GET /api/v1/temperature/deviation
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = TemperatureDeviationOverviewQuerySerializer(data=request.query_params)
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

        ds = TemperatureDeviationOverviewDependencyProvider.get_dep()

        data = get_temperature_deviation_overview(
            data_source=ds,
            **params,
        )

        full_payload = {
            "metadata": {
                "date_start": params["date_start"],
                "date_end": params["date_end"],
                "baseline": "1991-2020",
                "filters": {
                    "station_search": params.get("station_search"),
                    "station_ids": list(params.get("station_ids", ())),
                    "temperature_mean_min": params.get("temperature_mean_min"),
                    "temperature_mean_max": params.get("temperature_mean_max"),
                    "deviation_min": params.get("deviation_min"),
                    "deviation_max": params.get("deviation_max"),
                    "alt_min": params.get("alt_min"),
                    "alt_max": params.get("alt_max"),
                    "departments": list(params.get("departments", ())),
                    "regions": list(params.get("regions", ())),
                },
                "ordering": params.get("ordering", "-deviation"),
            },
            **data,
        }

        out = TemperatureDeviationOverviewResponseSerializer(data=full_payload)
        out.is_valid(raise_exception=True)

        return Response(out.data, status=status.HTTP_200_OK)
