import datetime as dt
from collections.abc import Callable

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


class FakeNationalIndicatorDataSource(
    NationalIndicatorObservedDataSource,
    NationalIndicatorBaselineDataSource,
):
    def __init__(self, day_to_temp_func: Callable[[dt.date], float]):
        self._day_to_temp = day_to_temp_func

    def fetch_daily_series(self, query: DailySeriesQuery) -> list[ObservedPoint]:
        if query.target_dates is not None:
            days = query.target_dates
        else:
            days = tuple(iter_days_intersecting(query.date_start, query.date_end))

        return [
            ObservedPoint(
                date=d,
                temperature=float(self._day_to_temp(d)),
            )
            for d in days
        ]

    def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
        mean = 1000.0 + float(day.day)
        return BaselinePoint(
            baseline_mean=mean,
            baseline_std_dev_upper=mean + 1.0,
            baseline_std_dev_lower=mean - 1.0,
            baseline_max=0.0,
            baseline_min=0.0,
        )

    def fetch_monthly_baseline(self, month: int) -> BaselinePoint:
        mean = 2000.0 + float(month)
        return BaselinePoint(
            baseline_mean=mean,
            baseline_std_dev_upper=mean + 1.0,
            baseline_std_dev_lower=mean - 1.0,
            baseline_max=0.0,
            baseline_min=0.0,
        )

    def fetch_yearly_baseline(self) -> BaselinePoint:
        mean = 3000.0
        return BaselinePoint(
            baseline_mean=mean,
            baseline_std_dev_upper=mean + 1.0,
            baseline_std_dev_lower=mean - 1.0,
            baseline_max=0.0,
            baseline_min=0.0,
        )


def test_itn_acceptance_month_day_of_month_clamp():
    ds = FakeNationalIndicatorDataSource(lambda d: d.day)

    res = compute_national_indicator(
        observed_data_source=ds,
        baseline_data_source=ds,
        date_start=dt.date(2025, 1, 1),
        date_end=dt.date(2025, 2, 28),
        granularity="month",
        slice_type="day_of_month",
        day_of_month=31,
    )

    ts = res["time_series"]

    assert len(ts) == 2

    assert ts[0]["date"] == dt.date(2025, 1, 31).isoformat()
    assert ts[1]["date"] == dt.date(2025, 2, 28).isoformat()

    assert ts[0]["temperature"] == 31.0
    assert ts[1]["temperature"] == 28.0

    # month + day_of_month => baseline journalière
    assert ts[0]["baseline_mean"] == 1031.0
    assert ts[1]["baseline_mean"] == 1028.0


def test_itn_acceptance_year_month_of_year_filters_correctly():
    ds = FakeNationalIndicatorDataSource(lambda d: 100.0 if d.month == 1 else 0.0)

    res = compute_national_indicator(
        observed_data_source=ds,
        baseline_data_source=ds,
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

    # year + month_of_year => baseline mensuelle
    assert ts[0]["baseline_mean"] == 2001.0
    assert ts[1]["baseline_mean"] == 2001.0


def test_itn_acceptance_year_day_of_month_with_month_and_clamp_leap_year():
    ds = FakeNationalIndicatorDataSource(lambda d: d.day)

    res = compute_national_indicator(
        observed_data_source=ds,
        baseline_data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2025, 12, 31),
        granularity="year",
        slice_type="day_of_month",
        month_of_year=2,
        day_of_month=31,
    )

    ts = res["time_series"]

    assert len(ts) == 2

    assert ts[0]["date"] == dt.date(2024, 2, 29).isoformat()  # bissextile
    assert ts[1]["date"] == dt.date(2025, 2, 28).isoformat()  # non bissextile

    assert ts[0]["temperature"] == 29.0
    assert ts[1]["temperature"] == 28.0

    # year + day_of_month => baseline journalière sur la date réelle après clamp
    assert ts[0]["baseline_mean"] == 1029.0
    assert ts[1]["baseline_mean"] == 1028.0
