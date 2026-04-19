"""
Root URL configuration for meteo-api.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from weather.metrics import metrics_view

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # Prometheus metrics
    path("metrics/", metrics_view, name="metrics"),
    # API v1
    path("api/v1/", include("weather.urls")),
    # OpenAPI schema and documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
