"""
URL routing for weather API endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AbsoluteRecordsGraphAPIView,
    NationalIndicatorAPIView,
    NationalIndicatorKpiAPIView,
    RecordsGraphAPIView,
    StationViewSet,
    TemperatureAbsoluteRecordsAPIView,
    TemperatureDeviationGraphAPIView,
    TemperatureDeviationOverviewAPIView,
    TemperatureMinMaxGraphAPIView,
    TemperatureRecordsAPIView,
)

router = DefaultRouter()
router.register(r"stations", StationViewSet, basename="station")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "temperature/national-indicator",
        NationalIndicatorAPIView.as_view(),
        name="temperature-national-indicator",
    ),
    path(
        "temperature/national-indicator/kpi",
        NationalIndicatorKpiAPIView.as_view(),
        name="temperature-national-indicator-kpi",
    ),
    path(
        "temperature/records",
        TemperatureRecordsAPIView.as_view(),
        name="temperature-records",
    ),
    path(
        "temperature/records/historical",
        TemperatureRecordsAPIView.as_view(),
        name="temperature-records-historical",
    ),
    path(
        "temperature/records/absolute",
        TemperatureAbsoluteRecordsAPIView.as_view(),
        name="temperature-records-absolute",
    ),
    path(
        "temperature/records/graph",
        RecordsGraphAPIView.as_view(),
        name="temperature-records-graph",
    ),
    path(
        "temperature/records/historical/graph",
        RecordsGraphAPIView.as_view(),
        name="temperature-records-historical-graph",
    ),
    path(
        "temperature/records/absolute/graph",
        AbsoluteRecordsGraphAPIView.as_view(),
        name="temperature-records-absolute-graph",
    ),
    path(
        "temperature/deviation",
        TemperatureDeviationOverviewAPIView.as_view(),
        name="temperature-deviation-overview",
    ),
    path(
        "temperature/deviation/graph",
        TemperatureDeviationGraphAPIView.as_view(),
        name="temperature-deviation-graph",
    ),
    path(
        "temperature/extremes/graph",
        TemperatureMinMaxGraphAPIView.as_view(),
        name="temperature-extremes-graph",
    ),
]
