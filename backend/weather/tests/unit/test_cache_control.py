"""Tests unitaires de ``CacheControlMixin``.

On teste le mixin de bout en bout via une ``APIView`` factice et
``APIRequestFactory``, plus des cas ciblés sur ``_compute_cache_ttls`` pour
les branches difficiles à reproduire en intégration (date_end illisible).
"""

from __future__ import annotations

import datetime as dt

import pytest
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from weather.cache_control import CacheControlMixin

FIXED_TODAY = dt.date(2026, 5, 22)


def _make_view(**class_attrs):
    """Construit une APIView factice utilisant le mixin avec les attributs voulus."""

    fixed_today = class_attrs.pop("_today_returns", FIXED_TODAY)

    class _DummyView(CacheControlMixin, APIView):
        authentication_classes: list = []
        permission_classes: list = []

        def get(self, request, *args, **kwargs):  # pragma: no cover - trivial
            return Response({"ok": True}, status=200)

        def _today(self) -> dt.date:
            return fixed_today

    for name, value in class_attrs.items():
        setattr(_DummyView, name, value)

    return _DummyView


@pytest.fixture
def factory():
    return APIRequestFactory()


def _cache_control(response) -> str | None:
    return response.get("Cache-Control")


class TestNoProfile:
    def test_no_header_when_profile_is_none(self, factory):
        view = _make_view(cache_profile=None).as_view()
        response = view(factory.get("/whatever"))
        assert _cache_control(response) is None


class TestLongProfile:
    def test_long_ttl_uses_class_defaults(self, factory):
        view = _make_view(cache_profile="long").as_view()
        response = view(factory.get("/whatever"))
        assert _cache_control(response) == "public, s-maxage=86400, max-age=3600"

    def test_long_ttl_respects_per_view_overrides(self, factory):
        view = _make_view(
            cache_profile="long",
            cache_long_s_maxage=604_800,
            cache_long_max_age=3_600,
        ).as_view()
        response = view(factory.get("/stations"))
        assert _cache_control(response) == "public, s-maxage=604800, max-age=3600"

    def test_long_profile_ignores_date_end(self, factory):
        """Le profil long ne lit pas date_end : TTL long quoi qu'il arrive."""
        view = _make_view(cache_profile="long").as_view()
        response = view(factory.get(f"/x?date_end={FIXED_TODAY.isoformat()}"))
        assert _cache_control(response) == "public, s-maxage=86400, max-age=3600"


class TestByDateEndProfile:
    def test_no_date_end_falls_back_to_long(self, factory):
        view = _make_view(cache_profile="by_date_end").as_view()
        response = view(factory.get("/x"))
        assert _cache_control(response) == "public, s-maxage=86400, max-age=3600"

    def test_historical_date_end_is_long(self, factory):
        view = _make_view(cache_profile="by_date_end").as_view()
        historical = (FIXED_TODAY - dt.timedelta(days=30)).isoformat()
        response = view(factory.get(f"/x?date_end={historical}"))
        assert _cache_control(response) == "public, s-maxage=86400, max-age=3600"

    def test_today_date_end_is_short(self, factory):
        view = _make_view(cache_profile="by_date_end").as_view()
        response = view(factory.get(f"/x?date_end={FIXED_TODAY.isoformat()}"))
        assert _cache_control(response) == "public, s-maxage=900, max-age=60"

    def test_yesterday_date_end_is_short(self, factory):
        """J-1 est dans la "zone d'ingestion incertaine" → court."""
        view = _make_view(cache_profile="by_date_end").as_view()
        yesterday = (FIXED_TODAY - dt.timedelta(days=1)).isoformat()
        response = view(factory.get(f"/x?date_end={yesterday}"))
        assert _cache_control(response) == "public, s-maxage=900, max-age=60"

    def test_boundary_is_strict_less_than(self, factory):
        """date_end == today − threshold_days est en zone "récente" (court)."""
        view = _make_view(cache_profile="by_date_end").as_view()
        boundary = (FIXED_TODAY - dt.timedelta(days=2)).isoformat()
        response = view(factory.get(f"/x?date_end={boundary}"))
        assert _cache_control(response) == "public, s-maxage=900, max-age=60"

    def test_threshold_customizable(self, factory):
        """Avec un threshold de 7 jours, J-3 doit être considéré comme récent."""
        view = _make_view(
            cache_profile="by_date_end",
            cache_date_end_threshold_days=7,
        ).as_view()
        date_end = (FIXED_TODAY - dt.timedelta(days=3)).isoformat()
        response = view(factory.get(f"/x?date_end={date_end}"))
        assert _cache_control(response) == "public, s-maxage=900, max-age=60"

    def test_malformed_date_end_falls_back_to_short(self, factory):
        """Branche défensive : malgré le 400 attendu côté serializer, on ne
        casse pas si une 200 remonte avec un date_end illisible."""
        view = _make_view(cache_profile="by_date_end").as_view()
        response = view(factory.get("/x?date_end=not-a-date"))
        assert _cache_control(response) == "public, s-maxage=900, max-age=60"


class TestHeaderGuards:
    def test_no_header_on_400(self, factory):
        class _Erroring(CacheControlMixin, APIView):
            authentication_classes: list = []
            permission_classes: list = []
            cache_profile = "long"

            def get(self, request, *args, **kwargs):
                return Response({"err": "x"}, status=400)

        response = _Erroring.as_view()(factory.get("/x"))
        assert _cache_control(response) is None

    def test_no_header_on_options(self, factory):
        view = _make_view(cache_profile="long").as_view()
        response = view(factory.options("/x"))
        assert _cache_control(response) is None
