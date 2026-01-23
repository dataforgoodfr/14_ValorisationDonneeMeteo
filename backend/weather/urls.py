"""
URL routing for weather API endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HoraireTempsReelViewSet, QuotidienneViewSet, StationViewSet

router = DefaultRouter()
router.register(r"stations", StationViewSet, basename="station")
router.register(r"horaire", HoraireTempsReelViewSet, basename="horaire")
router.register(r"quotidien", QuotidienneViewSet, basename="quotidien")

urlpatterns = [
    path("", include(router.urls)),
]
