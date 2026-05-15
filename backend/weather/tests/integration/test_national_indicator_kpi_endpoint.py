"""
Tests de l'endpoint GET /api/v1/temperature/national-indicator/kpi.

Couvre uniquement la couche HTTP : URL, validation des paramètres,
serialisation, et passage du résultat depuis le data source vers la réponse.

La logique métier (peak/jour au-dessus/itn_mean/etc.) est testée séparément
via le data source SQL — voir test_national_indicator_kpi_timescale_datasource_business.py.
"""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from weather.bootstrap_itn_kpi import ITNKpiDependencyProvider
from weather.services.national_indicator.protocols import (
    NationalIndicatorKpiDataSource,
)
from weather.services.national_indicator.types import (
    KpiPeriodStats,
    NationalIndicatorKpiResult,
)


class _StubKpiDataSource(NationalIndicatorKpiDataSource):
    """Renvoie un résultat figé, indépendant des arguments."""

    def __init__(self, result: NationalIndicatorKpiResult) -> None:
        self._result = result

    def compute_kpi(self, **_) -> NationalIndicatorKpiResult:
        return self._result


def _register(result: NationalIndicatorKpiResult) -> None:
    ITNKpiDependencyProvider.set_builder(lambda: _StubKpiDataSource(result))


def _stats(
    *,
    hot: int = 0,
    cold: int = 0,
    above: int = 0,
    below: int = 0,
    itn_mean: float | None = None,
    deviation: float | None = None,
) -> KpiPeriodStats:
    return KpiPeriodStats(
        hot_peak_count=hot,
        cold_peak_count=cold,
        days_above_baseline=above,
        days_below_baseline=below,
        itn_mean=itn_mean,
        deviation_from_normal=deviation,
    )


@pytest.fixture(autouse=True)
def reset_itn_kpi_dependency_provider() -> None:
    ITNKpiDependencyProvider.reset()
    yield
    ITNKpiDependencyProvider.reset()


# ---------------------------------------------------------------------------
# Sérialisation : le data source nous donne X, on le retrouve dans la réponse
# ---------------------------------------------------------------------------


def test_kpi_endpoint_serializes_current_period_stats(client: APIClient) -> None:
    _register(
        NationalIndicatorKpiResult(
            current=_stats(
                hot=3,
                cold=1,
                above=10,
                below=5,
                itn_mean=11.0,
                deviation=1.0,
            ),
            previous=_stats(),
        )
    )

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-31"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["hot_peak_count"] == 3
    assert data["cold_peak_count"] == 1
    assert data["days_above_baseline"] == 10
    assert data["days_below_baseline"] == 5
    assert data["itn_mean"] == pytest.approx(11.0)
    assert data["deviation_from_normal"] == pytest.approx(1.0)


def test_kpi_endpoint_response_contains_previous_field(client: APIClient) -> None:
    _register(
        NationalIndicatorKpiResult(
            current=_stats(),
            previous=_stats(
                hot=2, cold=4, above=7, below=3, itn_mean=9.0, deviation=-1.0
            ),
        )
    )

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-31"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "previous" in data
    assert data["previous"]["hot_peak_count"] == 2
    assert data["previous"]["cold_peak_count"] == 4
    assert data["previous"]["days_above_baseline"] == 7
    assert data["previous"]["days_below_baseline"] == 3
    assert data["previous"]["itn_mean"] == pytest.approx(9.0)
    assert data["previous"]["deviation_from_normal"] == pytest.approx(-1.0)


def test_kpi_endpoint_null_itn_mean_and_deviation_are_serialized_as_null(
    client: APIClient,
) -> None:
    _register(
        NationalIndicatorKpiResult(
            current=_stats(itn_mean=None, deviation=None),
            previous=_stats(itn_mean=None, deviation=None),
        )
    )

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-31"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["itn_mean"] is None
    assert data["deviation_from_normal"] is None
    assert data["previous"]["itn_mean"] is None
    assert data["previous"]["deviation_from_normal"] is None


# ---------------------------------------------------------------------------
# Validation des paramètres
# ---------------------------------------------------------------------------


def test_kpi_endpoint_missing_date_start_returns_400(client: APIClient) -> None:
    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_end": "2024-01-31"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"


def test_kpi_endpoint_date_start_after_date_end_returns_400(client: APIClient) -> None:
    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-02-01", "date_end": "2024-01-01"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"
