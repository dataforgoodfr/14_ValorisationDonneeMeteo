from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from weather.bootstrap_itn import ITNDependencies, ITNDependencyProvider
from weather.services.national_indicator.protocols import (
    NationalIndicatorAbsoluteExtremesDataSource,
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.types import (
    AbsoluteExtremes,
    BaselinePoint,
    DailySeriesQuery,
    ObservedPoint,
)
from weather.tests.helpers.itn_absolute_extremes import stub_absolute_extremes
from weather.utils.date_range import iter_days_intersecting


@pytest.fixture(autouse=True)
def reset_itn_dependency_provider():
    ITNDependencyProvider.reset()
    yield
    ITNDependencyProvider.reset()


def test_get_national_indicator_month_happy_path(client: APIClient):
    class InMemoryITNDependency(
        NationalIndicatorObservedDataSource,
        NationalIndicatorBaselineDataSource,
    ):
        def fetch_daily_series(self, query: DailySeriesQuery) -> list[ObservedPoint]:
            if query.target_dates is not None:
                days = query.target_dates
            else:
                days = tuple(iter_days_intersecting(query.date_start, query.date_end))

            out: list[ObservedPoint] = []
            for d in days:
                temp = 2.0 if d == dt.date(2025, 1, 1) else 1.0
                out.append(
                    ObservedPoint(
                        date=d,
                        temperature=temp,
                    )
                )
            return out

        def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
            mean = 1000.0 + float(day.day)
            return BaselinePoint(
                baseline_mean=mean,
                baseline_std_dev_upper=mean + 1.0,
                baseline_std_dev_lower=mean - 1.0,
            )

        def fetch_monthly_baseline(self, month: int) -> BaselinePoint:
            mean = 2000.0 + float(month)
            return BaselinePoint(
                baseline_mean=mean,
                baseline_std_dev_upper=mean + 1.0,
                baseline_std_dev_lower=mean - 1.0,
            )

        def fetch_yearly_baseline(self) -> BaselinePoint:
            mean = 3000.0
            return BaselinePoint(
                baseline_mean=mean,
                baseline_std_dev_upper=mean + 1.0,
                baseline_std_dev_lower=mean - 1.0,
            )

    ITNDependencyProvider.set_builder(
        lambda: ITNDependencies(
            observed_data_source=InMemoryITNDependency(),
            baseline_data_source=InMemoryITNDependency(),
            absolute_extremes_data_source=stub_absolute_extremes,
        )
    )

    url = reverse("temperature-national-indicator")
    resp = client.get(
        url,
        {
            "date_start": "2025-01-01",
            "date_end": "2025-01-31",
            "granularity": "month",
            "slice_type": "full",
        },
    )

    assert resp.status_code == 200
    payload = resp.json()

    ts = payload["time_series"]
    assert len(ts) == 1

    expected_itn_month = (30 * 1.0 + 2.0) / 31.0
    assert ts[0]["temperature"] == round(expected_itn_month, 2)

    # month + full => baseline mensuelle
    assert ts[0]["baseline_mean"] == 2001.0

    # température (≈1.06) << lower (1999.0) => cold peak
    assert ts[0]["is_cold_peak"] is True
    assert ts[0]["is_hot_peak"] is False


def test_get_national_indicator_peak_flags_in_response(client: APIClient):
    # baseline upper=12, lower=8 pour chaque jour
    _upper = 12.0
    _lower = 8.0
    _mean = 10.0

    class PeakTestDependency(
        NationalIndicatorObservedDataSource,
        NationalIndicatorBaselineDataSource,
    ):
        def fetch_daily_series(self, query: DailySeriesQuery) -> list[ObservedPoint]:
            days = query.target_dates or tuple(
                iter_days_intersecting(query.date_start, query.date_end)
            )
            temps = {
                dt.date(2025, 6, 1): _upper + 1.0,  # hot peak
                dt.date(2025, 6, 2): _mean,  # normal
                dt.date(2025, 6, 3): _lower - 1.0,  # cold peak
            }
            return [ObservedPoint(date=d, temperature=temps[d]) for d in days]

        def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
            return BaselinePoint(
                baseline_mean=_mean,
                baseline_std_dev_upper=_upper,
                baseline_std_dev_lower=_lower,
            )

        def fetch_monthly_baseline(self, month: int) -> BaselinePoint:
            return self.fetch_daily_baseline(dt.date(2025, month, 1))

        def fetch_yearly_baseline(self) -> BaselinePoint:
            return self.fetch_daily_baseline(dt.date(2025, 1, 1))

    ITNDependencyProvider.set_builder(
        lambda: ITNDependencies(
            observed_data_source=PeakTestDependency(),
            baseline_data_source=PeakTestDependency(),
            absolute_extremes_data_source=stub_absolute_extremes,
        )
    )

    url = reverse("temperature-national-indicator")
    resp = client.get(
        url,
        {
            "date_start": "2025-06-01",
            "date_end": "2025-06-03",
            "granularity": "day",
        },
    )

    assert resp.status_code == 200
    ts = resp.json()["time_series"]
    assert len(ts) == 3

    assert ts[0]["is_hot_peak"] is True
    assert ts[0]["is_cold_peak"] is False

    assert ts[1]["is_hot_peak"] is False
    assert ts[1]["is_cold_peak"] is False

    assert ts[2]["is_hot_peak"] is False
    assert ts[2]["is_cold_peak"] is True


def test_get_national_indicator_missing_required_parameter_returns_400(
    client: APIClient,
):
    url = reverse("temperature-national-indicator")

    resp = client.get(
        url,
        {
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            # granularity manquant
        },
    )

    assert resp.status_code == 400

    data = resp.json()

    assert "error" in data
    assert data["error"]["code"] == "INVALID_PARAMETER"
    assert "granularity" in data["error"]["details"]


def test_get_national_indicator_invalid_combination_returns_400(client: APIClient):
    url = reverse("temperature-national-indicator")

    resp = client.get(
        url,
        {
            "date_start": "2024-01-01",
            "date_end": "2024-01-07",
            "granularity": "day",
            "slice_type": "day_of_month",
            "day_of_month": 1,
        },
    )

    assert resp.status_code == 400

    data = resp.json()

    assert "error" in data
    assert data["error"]["code"] == "INVALID_PARAMETER"
    assert "slice_type" in data["error"]["details"]


def test_get_national_indicator_response_contains_absolute_extremes(client: APIClient):
    """Les champs absolute_min et absolute_max sont présents dans chaque entrée time_series."""

    class InMemoryWithAbsoluteExtremes(
        NationalIndicatorObservedDataSource,
        NationalIndicatorBaselineDataSource,
    ):
        def fetch_daily_series(self, query: DailySeriesQuery) -> list[ObservedPoint]:
            days = query.target_dates or tuple(
                iter_days_intersecting(query.date_start, query.date_end)
            )
            return [ObservedPoint(date=d, temperature=10.0) for d in days]

        def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
            return BaselinePoint(
                baseline_mean=10.0,
                baseline_std_dev_upper=12.0,
                baseline_std_dev_lower=8.0,
            )

        def fetch_monthly_baseline(self, month: int) -> BaselinePoint:
            return self.fetch_daily_baseline(dt.date(2025, month, 1))

        def fetch_yearly_baseline(self) -> BaselinePoint:
            return self.fetch_daily_baseline(dt.date(2025, 1, 1))

    class FixedAbsoluteExtremes(NationalIndicatorAbsoluteExtremesDataSource):
        def fetch_daily_absolute_extremes(
            self, month_day_pairs: set[tuple[int, int]]
        ) -> dict[tuple[int, int], AbsoluteExtremes]:
            return {
                k: AbsoluteExtremes(absolute_min=-5.0, absolute_max=30.0)
                for k in month_day_pairs
            }

        def fetch_monthly_absolute_extremes(
            self, months: set[int]
        ) -> dict[int, AbsoluteExtremes]:
            return {
                m: AbsoluteExtremes(absolute_min=-5.0, absolute_max=30.0)
                for m in months
            }

        def fetch_yearly_absolute_extremes(self) -> AbsoluteExtremes:
            return AbsoluteExtremes(absolute_min=-5.0, absolute_max=30.0)

    dep = InMemoryWithAbsoluteExtremes()
    extremes = FixedAbsoluteExtremes()
    ITNDependencyProvider.set_builder(
        lambda: ITNDependencies(
            observed_data_source=dep,
            baseline_data_source=dep,
            absolute_extremes_data_source=extremes,
        )
    )

    url = reverse("temperature-national-indicator")
    resp = client.get(
        url,
        {"date_start": "2025-01-01", "date_end": "2025-01-03", "granularity": "day"},
    )

    assert resp.status_code == 200
    ts = resp.json()["time_series"]
    assert len(ts) == 3

    for point in ts:
        assert "baseline_min" in point
        assert "baseline_max" in point
        assert point["baseline_min"] == -5.0
        assert point["baseline_max"] == 30.0
