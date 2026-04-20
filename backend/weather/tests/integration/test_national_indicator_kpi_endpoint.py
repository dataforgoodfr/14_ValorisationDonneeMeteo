from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from weather.bootstrap_itn import ITNDependencies, ITNDependencyProvider
from weather.services.national_indicator.protocols import (
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.types import (
    BaselinePoint,
    DailySeriesQuery,
    ObservedPoint,
)


@pytest.fixture(autouse=True)
def reset_itn_dependency_provider():
    ITNDependencyProvider.reset()
    yield
    ITNDependencyProvider.reset()


class InMemoryKpiDependency(
    NationalIndicatorObservedDataSource,
    NationalIndicatorBaselineDataSource,
):
    """
    Dépendance en mémoire pour les tests KPI.
    Baseline : mean=10.0, std_dev band de ±2.0 → upper=12.0, lower=8.0
    Températures : fournies via le dictionnaire `temps` (date → valeur).
    """

    def __init__(self, temps: dict[dt.date, float]):
        self._temps = temps

    def fetch_daily_series(self, query: DailySeriesQuery) -> list[ObservedPoint]:
        start, end = query.date_start, query.date_end
        return [
            ObservedPoint(date=d, temperature=self._temps.get(d, 10.0))
            for d in (
                start + dt.timedelta(days=i) for i in range((end - start).days + 1)
            )
        ]

    def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
        return BaselinePoint(
            baseline_mean=10.0,
            baseline_std_dev_upper=12.0,
            baseline_std_dev_lower=8.0,
            baseline_max=15.0,
            baseline_min=5.0,
        )


def _register(temps: dict[dt.date, float]) -> None:
    dep = InMemoryKpiDependency(temps)
    ITNDependencyProvider.set_builder(
        lambda: ITNDependencies(
            observed_data_source=dep,
            baseline_data_source=dep,
        )
    )


# ---------------------------------------------------------------------------
# Cas nominaux
# ---------------------------------------------------------------------------


def test_kpi_hot_returns_only_days_above_upper_std_dev(client: APIClient):
    # Seul le 3 jan dépasse upper (12.0)
    temps = {
        dt.date(2024, 1, 1): 10.0,
        dt.date(2024, 1, 2): 11.5,
        dt.date(2024, 1, 3): 13.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03", "type": "hot"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["days"][0]["date"] == "2024-01-03"
    assert data["days"][0]["temperature"] == 13.0


def test_kpi_cold_returns_only_days_below_lower_std_dev(client: APIClient):
    # Seul le 2 jan est sous lower (8.0)
    temps = {
        dt.date(2024, 1, 1): 9.0,
        dt.date(2024, 1, 2): 7.0,
        dt.date(2024, 1, 3): 10.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03", "type": "cold"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 1
    assert data["days"][0]["date"] == "2024-01-02"
    assert data["days"][0]["temperature"] == 7.0


def test_kpi_no_peak_returns_empty_list(client: APIClient):
    # Toutes les températures dans la plage normale
    _register({})  # toutes les dates → 10.0 (= mean)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-05", "type": "hot"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0
    assert data["days"] == []


def test_kpi_multiple_peaks_all_returned(client: APIClient):
    temps = {
        dt.date(2024, 6, 1): 14.0,
        dt.date(2024, 6, 2): 10.0,
        dt.date(2024, 6, 3): 15.0,
        dt.date(2024, 6, 4): 9.0,
        dt.date(2024, 6, 5): 13.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-06-01", "date_end": "2024-06-05", "type": "hot"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 3
    dates = [d["date"] for d in data["days"]]
    assert "2024-06-01" in dates
    assert "2024-06-03" in dates
    assert "2024-06-05" in dates


def test_kpi_response_contains_baseline_mean_and_std_dev(client: APIClient):
    _register({dt.date(2024, 1, 1): 13.0})

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-01", "type": "hot"},
    )

    assert resp.status_code == 200
    day = resp.json()["days"][0]
    assert day["baseline_mean"] == 10.0
    # std_dev = upper - mean = 12.0 - 10.0
    assert day["baseline_std_dev"] == 2.0


# ---------------------------------------------------------------------------
# Validation des paramètres
# ---------------------------------------------------------------------------


def test_kpi_missing_type_returns_400(client: APIClient):
    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-31"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"


def test_kpi_missing_date_start_returns_400(client: APIClient):
    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_end": "2024-01-31", "type": "hot"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"


def test_kpi_date_start_after_date_end_returns_400(client: APIClient):
    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-02-01", "date_end": "2024-01-01", "type": "hot"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"


def test_kpi_invalid_type_returns_400(client: APIClient):
    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-31", "type": "warm"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"
