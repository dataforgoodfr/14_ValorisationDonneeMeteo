import datetime as dt

import pytest

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorBaselineDataSource,
    TimescaleNationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.types import (
    DailySeriesQuery,
    ObservedSeriesQuery,
)
from weather.tests.helpers.itn import (
    clear_itn_daily_observed,
    insert_itn_daily_observed,
)
from weather.tests.helpers.itn_baseline import (
    insert_daily_baseline,
    insert_monthly_baseline,
    insert_yearly_baseline,
)

pytestmark = pytest.mark.django_db


# ----------------------------
# Observed datasource tests
# ----------------------------
def test_fetch_daily_series_reads_mv_itn_daily_observed():
    clear_itn_daily_observed()

    day = dt.date(2025, 1, 1)
    insert_itn_daily_observed(day, 12.5)

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_daily_series(
        DailySeriesQuery(
            date_start=day,
            date_end=day,
            target_dates=None,
        )
    )

    assert len(result) == 1
    assert result[0].date == day
    assert result[0].temperature == 12.5


def test_fetch_daily_series_filters_target_dates():
    clear_itn_daily_observed()

    d1 = dt.date(2025, 1, 1)
    d2 = dt.date(2025, 1, 2)

    insert_itn_daily_observed(d1, 10.0)
    insert_itn_daily_observed(d2, 20.0)

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_daily_series(
        DailySeriesQuery(
            date_start=d1,
            date_end=d2,
            target_dates=(d2,),
        )
    )

    assert len(result) == 1
    assert result[0].date == d2
    assert result[0].temperature == 20.0


def test_fetch_observed_series_month_full_aggregates_in_sql():
    clear_itn_daily_observed()

    insert_itn_daily_observed(dt.date(2025, 1, 1), 10.0)
    insert_itn_daily_observed(dt.date(2025, 1, 2), 20.0)
    insert_itn_daily_observed(dt.date(2025, 2, 1), 30.0)

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2025, 1, 1),
            date_end=dt.date(2025, 2, 28),
            granularity="month",
            slice_type="full",
        )
    )

    assert [(p.date, p.temperature) for p in result] == [
        (dt.date(2025, 1, 1), pytest.approx(15.0)),
        (dt.date(2025, 2, 1), pytest.approx(30.0)),
    ]


def test_fetch_observed_series_year_full_aggregates_in_sql():
    clear_itn_daily_observed()

    insert_itn_daily_observed(dt.date(2024, 1, 1), 10.0)
    insert_itn_daily_observed(dt.date(2024, 12, 31), 20.0)
    insert_itn_daily_observed(dt.date(2025, 1, 1), 30.0)

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2024, 1, 1),
            date_end=dt.date(2025, 12, 31),
            granularity="year",
            slice_type="full",
        )
    )

    assert [(p.date, p.temperature) for p in result] == [
        (dt.date(2024, 1, 1), pytest.approx(15.0)),
        (dt.date(2025, 1, 1), pytest.approx(30.0)),
    ]


def test_fetch_observed_series_year_month_of_year():
    clear_itn_daily_observed()

    insert_itn_daily_observed(dt.date(2024, 1, 1), 10.0)
    insert_itn_daily_observed(dt.date(2024, 2, 1), 100.0)
    insert_itn_daily_observed(dt.date(2025, 1, 1), 20.0)
    insert_itn_daily_observed(dt.date(2025, 2, 1), 200.0)

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2024, 1, 1),
            date_end=dt.date(2025, 12, 31),
            granularity="year",
            slice_type="month_of_year",
            month_of_year=1,
        )
    )

    assert [(p.date, p.temperature) for p in result] == [
        (dt.date(2024, 1, 1), pytest.approx(10.0)),
        (dt.date(2025, 1, 1), pytest.approx(20.0)),
    ]


def test_fetch_observed_series_month_day_of_month_uses_target_dates():
    clear_itn_daily_observed()

    insert_itn_daily_observed(dt.date(2025, 1, 31), 31.0)
    insert_itn_daily_observed(dt.date(2025, 2, 28), 28.0)
    insert_itn_daily_observed(dt.date(2025, 2, 27), 999.0)

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2025, 1, 1),
            date_end=dt.date(2025, 2, 28),
            granularity="month",
            slice_type="day_of_month",
            day_of_month=31,
            target_dates=(
                dt.date(2025, 1, 31),
                dt.date(2025, 2, 28),
            ),
        )
    )

    assert [(p.date, p.temperature) for p in result] == [
        (dt.date(2025, 1, 1), pytest.approx(31.0)),
        (dt.date(2025, 2, 1), pytest.approx(28.0)),
    ]


def test_fetch_observed_series_year_day_of_month_uses_target_dates():
    clear_itn_daily_observed()

    insert_itn_daily_observed(dt.date(2024, 2, 29), 29.0)
    insert_itn_daily_observed(dt.date(2025, 2, 28), 28.0)
    insert_itn_daily_observed(dt.date(2025, 2, 27), 999.0)

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2024, 2, 1),
            date_end=dt.date(2025, 2, 28),
            granularity="year",
            slice_type="day_of_month",
            month_of_year=2,
            day_of_month=31,
            target_dates=(
                dt.date(2024, 2, 29),
                dt.date(2025, 2, 28),
            ),
        )
    )

    assert [(p.date, p.temperature) for p in result] == [
        (dt.date(2024, 2, 29), pytest.approx(29.0)),
        (dt.date(2025, 2, 28), pytest.approx(28.0)),
    ]


def test_fetch_observed_series_year_month_of_year_with_target_dates_binds_month_param():
    clear_itn_daily_observed()

    insert_itn_daily_observed(dt.date(2024, 1, 1), 10.0)
    insert_itn_daily_observed(dt.date(2024, 1, 2), 20.0)
    insert_itn_daily_observed(dt.date(2025, 1, 1), 30.0)
    insert_itn_daily_observed(dt.date(2025, 1, 2), 40.0)

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2024, 1, 1),
            date_end=dt.date(2025, 1, 31),
            granularity="year",
            slice_type="month_of_year",
            month_of_year=1,
            target_dates=(
                dt.date(2024, 1, 1),
                dt.date(2024, 1, 2),
                dt.date(2025, 1, 1),
                dt.date(2025, 1, 2),
            ),
        )
    )

    assert [(p.date, p.temperature) for p in result] == [
        (dt.date(2024, 1, 1), pytest.approx(15.0)),
        (dt.date(2025, 1, 1), pytest.approx(35.0)),
    ]


# ----------------------------
# Baseline datasource tests
# ----------------------------


def test_fetch_daily_baseline_happy_path():
    ds = TimescaleNationalIndicatorBaselineDataSource()

    insert_daily_baseline(month=1, day=15, mean=10.0, std=2.0)

    result = ds.fetch_daily_baseline(dt.date(2025, 1, 15))

    assert result.baseline_mean == 10.0
    assert result.baseline_std_dev_upper == 12.0
    assert result.baseline_std_dev_lower == 8.0


def test_fetch_monthly_baseline_happy_path():
    ds = TimescaleNationalIndicatorBaselineDataSource()

    insert_monthly_baseline(month=2, mean=20.0, std=3.0)

    result = ds.fetch_monthly_baseline(2)

    assert result.baseline_mean == 20.0
    assert result.baseline_std_dev_upper == 23.0
    assert result.baseline_std_dev_lower == 17.0


def test_fetch_yearly_baseline_happy_path():
    ds = TimescaleNationalIndicatorBaselineDataSource()

    insert_yearly_baseline(sample_size=30, mean=30.0, std=4.0)

    result = ds.fetch_yearly_baseline()

    assert result.baseline_mean == 30.0
    assert result.baseline_std_dev_upper == 34.0
    assert result.baseline_std_dev_lower == 26.0
