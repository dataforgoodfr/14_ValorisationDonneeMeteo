"""
URL routing for weather API endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    NationalIndicatorAPIView,
    NationalIndicatorKpiAPIView,
    StationViewSet,
    TemperatureDeviationGraphAPIView,
    TemperatureDeviationOverviewAPIView,
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
        "temperature/deviation/graph",
        TemperatureDeviationGraphAPIView.as_view(),
        name="temperature-deviation-graph",
    ),
    path(
        "temperature/deviation",
        TemperatureDeviationOverviewAPIView.as_view(),
        name="temperature-deviation-overview",
    ),
]
