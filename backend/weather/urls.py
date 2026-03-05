"""
URL routing for weather API endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    NationalIndicatorAPIView,
    StationViewSet,
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
]
