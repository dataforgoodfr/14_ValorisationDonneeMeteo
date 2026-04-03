"""
URL routing for weather API endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    NationalIndicatorAPIView,
    RecordsAPIView,
    StationViewSet,
    TemperatureDeviationAPIView,
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
        "temperature/records",
        RecordsAPIView.as_view(),
        name="records",
    ),
    path(
        "temperature/deviation",
        TemperatureDeviationAPIView.as_view(),
        name="temperature-deviation",
    ),
]
