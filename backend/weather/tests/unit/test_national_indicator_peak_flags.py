from __future__ import annotations

import datetime as dt

from weather.services.national_indicator.protocols import (
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.service import compute_national_indicator
from weather.services.national_indicator.types import (
    BaselinePoint,
    DailySeriesQuery,
    ObservedPoint,
)
from weather.utils.date_range import iter_days_intersecting

# baseline_mean=10, std_dev=2 => upper=12, lower=8
_BASELINE_MEAN = 10.0
_BASELINE_STD_DEV = 2.0
_UPPER = _BASELINE_MEAN + _BASELINE_STD_DEV  # 12.0
_LOWER = _BASELINE_MEAN - _BASELINE_STD_DEV  # 8.0


class FixedBaselineDataSource(
    NationalIndicatorObservedDataSource,
    NationalIndicatorBaselineDataSource,
):
    def __init__(self, day_to_temp: dict[dt.date, float]):
        self._temps = day_to_temp

    def fetch_daily_series(self, query: DailySeriesQuery) -> list[ObservedPoint]:
        days = query.target_dates or tuple(
            iter_days_intersecting(query.date_start, query.date_end)
        )
        return [ObservedPoint(date=d, temperature=self._temps[d]) for d in days]

    def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
        return BaselinePoint(
            baseline_mean=_BASELINE_MEAN,
            baseline_std_dev_upper=_UPPER,
            baseline_std_dev_lower=_LOWER,
            baseline_max=0.0,
            baseline_min=0.0,
        )

    def fetch_monthly_baseline(self, month: int) -> BaselinePoint:
        return self.fetch_daily_baseline(dt.date(2025, month, 1))

    def fetch_yearly_baseline(self) -> BaselinePoint:
        return self.fetch_daily_baseline(dt.date(2025, 1, 1))


def _run(temps: dict[dt.date, float]) -> list[dict]:
    ds = FixedBaselineDataSource(temps)
    date_start = min(temps)
    date_end = max(temps)
    res = compute_national_indicator(
        observed_data_source=ds,
        baseline_data_source=ds,
        date_start=date_start,
        date_end=date_end,
        granularity="day",
    )
    return res["time_series"]


def test_temperature_above_upper_is_hot_peak():
    day = dt.date(2025, 6, 1)
    ts = _run({day: _UPPER + 0.01})
    assert ts[0]["is_hot_peak"] is True
    assert ts[0]["is_cold_peak"] is False


def test_temperature_below_lower_is_cold_peak():
    day = dt.date(2025, 6, 1)
    ts = _run({day: _LOWER - 0.01})
    assert ts[0]["is_hot_peak"] is False
    assert ts[0]["is_cold_peak"] is True


def test_temperature_equal_upper_is_not_hot_peak():
    day = dt.date(2025, 6, 1)
    ts = _run({day: _UPPER})
    assert ts[0]["is_hot_peak"] is False


def test_temperature_equal_lower_is_not_cold_peak():
    day = dt.date(2025, 6, 1)
    ts = _run({day: _LOWER})
    assert ts[0]["is_cold_peak"] is False


def test_temperature_within_bounds_is_no_peak():
    day = dt.date(2025, 6, 1)
    ts = _run({day: _BASELINE_MEAN})
    assert ts[0]["is_hot_peak"] is False
    assert ts[0]["is_cold_peak"] is False


def test_multiple_days_peaks_are_independent():
    days = {
        dt.date(2025, 6, 1): _UPPER + 1.0,  # hot
        dt.date(2025, 6, 2): _BASELINE_MEAN,  # normal
        dt.date(2025, 6, 3): _LOWER - 1.0,  # cold
    }
    ts = _run(days)

    assert ts[0]["is_hot_peak"] is True
    assert ts[0]["is_cold_peak"] is False

    assert ts[1]["is_hot_peak"] is False
    assert ts[1]["is_cold_peak"] is False

    assert ts[2]["is_hot_peak"] is False
    assert ts[2]["is_cold_peak"] is True


def test_peak_flags_present_in_output_keys():
    day = dt.date(2025, 6, 1)
    ts = _run({day: _BASELINE_MEAN})
    assert "is_hot_peak" in ts[0]
    assert "is_cold_peak" in ts[0]
