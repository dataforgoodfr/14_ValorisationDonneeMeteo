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
    Baseline fixe : mean=10.0, upper=12.0, lower=8.0.
    Températures fournies par `temps`, défaut 10.0 pour les dates inconnues.
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
# Cas nominaux – période courante
# ---------------------------------------------------------------------------


def test_kpi_hot_returns_count_above_upper_std_dev(client: APIClient):
    # Seul le 3 jan dépasse upper (12.0)
    temps = {
        dt.date(2024, 1, 1): 10.0,
        dt.date(2024, 1, 2): 11.5,
        dt.date(2024, 1, 3): 13.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["hot_peak_count"] == 1
    assert data["cold_peak_count"] == 0


def test_kpi_cold_returns_count_below_lower_std_dev(client: APIClient):
    # Seul le 2 jan est sous lower (8.0)
    temps = {
        dt.date(2024, 1, 1): 9.0,
        dt.date(2024, 1, 2): 7.0,
        dt.date(2024, 1, 3): 10.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["cold_peak_count"] == 1
    assert data["hot_peak_count"] == 0


def test_kpi_hot_and_cold_returned_simultaneously(client: APIClient):
    temps = {
        dt.date(2024, 1, 1): 13.0,  # pic chaud (> 12.0)
        dt.date(2024, 1, 2): 10.0,  # normal
        dt.date(2024, 1, 3): 7.0,  # pic froid (< 8.0)
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["hot_peak_count"] == 1
    assert data["cold_peak_count"] == 1


def test_kpi_no_peak_returns_zero_counts(client: APIClient):
    _register({})  # toutes les dates → 10.0 (= mean, pas de pic)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-05"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["hot_peak_count"] == 0
    assert data["cold_peak_count"] == 0


def test_kpi_multiple_hot_peaks_all_counted(client: APIClient):
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
        {"date_start": "2024-06-01", "date_end": "2024-06-05"},
    )

    assert resp.status_code == 200
    assert resp.json()["hot_peak_count"] == 3


def test_kpi_days_above_and_below_baseline(client: APIClient):
    temps = {
        dt.date(2024, 1, 1): 11.0,  # > mean(10)
        dt.date(2024, 1, 2): 10.0,  # = mean
        dt.date(2024, 1, 3): 9.0,  # < mean
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["days_above_baseline"] == 1
    assert data["days_below_baseline"] == 1


# ---------------------------------------------------------------------------
# Période précédente
# ---------------------------------------------------------------------------


def test_kpi_response_contains_previous_field(client: APIClient):
    _register({})

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "previous" in data
    assert "hot_peak_count" in data["previous"]
    assert "cold_peak_count" in data["previous"]
    assert "days_above_baseline" in data["previous"]
    assert "days_below_baseline" in data["previous"]
    assert "itn_mean" in data["previous"]
    assert "deviation_from_normal" in data["previous"]


def test_kpi_previous_period_uses_correct_dates(client: APIClient):
    # current : 2024-01-04 → 2024-01-06 (3 jours)
    # previous : 2024-01-01 → 2024-01-03 (3 jours)
    temps = {
        dt.date(2024, 1, 1): 13.0,  # pic chaud dans la période précédente
        dt.date(2024, 1, 2): 10.0,
        dt.date(2024, 1, 3): 10.0,
        dt.date(2024, 1, 4): 10.0,
        dt.date(2024, 1, 5): 10.0,
        dt.date(2024, 1, 6): 10.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-04", "date_end": "2024-01-06"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["hot_peak_count"] == 0  # pas de pic dans la période courante
    assert data["previous"]["hot_peak_count"] == 1  # pic le 2024-01-01


def test_kpi_previous_period_independent_stats(client: APIClient):
    # current : 2024-01-02 (temp=13 → pic chaud)
    # previous : 2024-01-01 (temp=7 → pic froid)
    temps = {
        dt.date(2024, 1, 1): 7.0,
        dt.date(2024, 1, 2): 13.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-02", "date_end": "2024-01-02"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["hot_peak_count"] == 1
    assert data["cold_peak_count"] == 0
    assert data["previous"]["cold_peak_count"] == 1
    assert data["previous"]["hot_peak_count"] == 0


# ---------------------------------------------------------------------------
# Validation des paramètres
# ---------------------------------------------------------------------------


def test_kpi_missing_date_start_returns_400(client: APIClient):
    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_end": "2024-01-31"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"


def test_kpi_date_start_after_date_end_returns_400(client: APIClient):
    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-02-01", "date_end": "2024-01-01"},
    )

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"


# ---------------------------------------------------------------------------
# itn_mean / deviation_from_normal
# ---------------------------------------------------------------------------


def test_kpi_itn_mean_is_average_over_all_days(client: APIClient):
    temps = {
        dt.date(2024, 1, 1): 10.0,
        dt.date(2024, 1, 2): 10.0,
        dt.date(2024, 1, 3): 13.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["hot_peak_count"] == 1
    assert data["itn_mean"] == pytest.approx((10.0 + 10.0 + 13.0) / 3)


def test_kpi_deviation_from_normal(client: APIClient):
    # baseline mean=10.0, itn_mean = (10+10+13)/3 = 11.0, deviation = 1.0
    temps = {
        dt.date(2024, 1, 1): 10.0,
        dt.date(2024, 1, 2): 10.0,
        dt.date(2024, 1, 3): 13.0,
    }
    _register(temps)

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03"},
    )

    assert resp.status_code == 200
    assert resp.json()["deviation_from_normal"] == pytest.approx(1.0)


def test_kpi_itn_mean_is_null_when_no_observed_data(client: APIClient):
    class EmptyObservedDependency(
        NationalIndicatorObservedDataSource,
        NationalIndicatorBaselineDataSource,
    ):
        def fetch_daily_series(self, _query: DailySeriesQuery) -> list[ObservedPoint]:
            return []

        def fetch_daily_baseline(self, _day: dt.date) -> BaselinePoint:
            return BaselinePoint(
                baseline_mean=10.0,
                baseline_std_dev_upper=12.0,
                baseline_std_dev_lower=8.0,
                baseline_max=15.0,
                baseline_min=5.0,
            )

    dep = EmptyObservedDependency()
    ITNDependencyProvider.set_builder(
        lambda: ITNDependencies(observed_data_source=dep, baseline_data_source=dep)
    )

    resp = client.get(
        reverse("temperature-national-indicator-kpi"),
        {"date_start": "2024-01-01", "date_end": "2024-01-03"},
    )

    assert resp.status_code == 200
    assert resp.json()["itn_mean"] is None
    assert resp.json()["deviation_from_normal"] is None
