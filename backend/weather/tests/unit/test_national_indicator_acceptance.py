import datetime as dt
from collections.abc import Callable

from weather.services.national_indicator.protocols import (
    NationalIndicatorDailyDataSource,
)
from weather.services.national_indicator.service import compute_national_indicator
from weather.services.national_indicator.types import DailyPoint, DailySeriesQuery
from weather.utils.date_range import iter_days_intersecting


class FakeDailySeriesDS(NationalIndicatorDailyDataSource):
    def __init__(self, day_to_temp_func: Callable):
        self._day_to_temp = day_to_temp_func

    def fetch_daily_series(self, query: DailySeriesQuery) -> list[DailyPoint]:
        if query.target_dates is not None:
            days = query.target_dates
        else:
            days = tuple(iter_days_intersecting(query.date_start, query.date_end))

        return [
            DailyPoint(
                date=d,
                temperature=float(self._day_to_temp(d)),
                baseline_mean=0.0,
                baseline_std_dev_upper=0.0,
                baseline_std_dev_lower=0.0,
                baseline_max=0.0,
                baseline_min=0.0,
            )
            for d in days
        ]


def test_itn_acceptance_month_day_of_month_clamp():
    ds = FakeDailySeriesDS(lambda d: d.day)
    res = compute_national_indicator(
        data_source=ds,
        date_start=dt.date(2025, 1, 1),
        date_end=dt.date(2025, 2, 28),
        granularity="month",
        slice_type="day_of_month",
        day_of_month=31,
    )

    ts = res["time_series"]
    assert len(ts) == 2
    assert ts[0]["temperature"] == 31.0
    assert ts[1]["temperature"] == 28.0


def test_itn_acceptance_year_month_of_year_filters_correctly():
    ds = FakeDailySeriesDS(lambda d: 100 if d.month == 1 else 0)

    res = compute_national_indicator(
        data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2025, 12, 31),
        granularity="year",
        slice_type="month_of_year",
        month_of_year=1,
    )

    ts = res["time_series"]
    assert len(ts) == 2
    assert ts[0]["temperature"] == 100.0
    assert ts[1]["temperature"] == 100.0


def test_itn_acceptance_year_day_of_month_with_month_and_clamp_leap_year():
    ds = FakeDailySeriesDS(lambda d: d.day)
    res = compute_national_indicator(
        data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2025, 12, 31),
        granularity="year",
        slice_type="day_of_month",
        month_of_year=2,
        day_of_month=31,
    )

    ts = res["time_series"]
    assert len(ts) == 2
    assert ts[0]["date"] == dt.date(2024, 2, 29).isoformat()  # 2024 bissextile
    assert ts[1]["date"] == dt.date(2025, 2, 28).isoformat()  # 2025 non bissextile

    assert ts[0]["temperature"] == 29.0
    assert ts[1]["temperature"] == 28.0
