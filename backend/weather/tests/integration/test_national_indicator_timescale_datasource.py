import datetime as dt

import pytest
from django.db import connection

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorBaselineDataSource,
    TimescaleNationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.types import (
    ObservedSeriesQuery,
)
from weather.tests.helpers.itn import insert_complete_itn_day
from weather.tests.helpers.itn_baseline import (
    insert_daily_baseline,
    insert_monthly_baseline,
    insert_yearly_baseline,
)

pytestmark = pytest.mark.django_db


def refresh_itn_daily_observed_mv() -> None:
    with connection.cursor() as cur:
        cur.execute("REFRESH MATERIALIZED VIEW public.mv_itn_daily_observed;")


# ----------------------------
# Observed datasource tests
# ----------------------------
def test_fetch_observed_series_reads_mv_itn_daily_observed():
    day = dt.date(2025, 1, 1)
    insert_complete_itn_day(day, 12.5)
    refresh_itn_daily_observed_mv()
    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=day,
            date_end=day,
            granularity="day",
            slice_type="full",
            target_dates=None,
        )
    )

    assert len(result) == 1
    assert result[0].date == day
    assert result[0].temperature == 12.5


def test_fetch_observed_series_filters_target_dates():
    d1 = dt.date(2025, 1, 1)
    d2 = dt.date(2025, 1, 2)

    insert_complete_itn_day(d1, 10.0)
    insert_complete_itn_day(d2, 20.0)
    refresh_itn_daily_observed_mv()

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=d1,
            date_end=d2,
            granularity="day",
            slice_type="full",
            target_dates=(d2,),
        )
    )

    assert len(result) == 1
    assert result[0].date == d2
    assert result[0].temperature == 20.0


def test_fetch_observed_series_month_full_aggregates_in_sql():
    insert_complete_itn_day(dt.date(2025, 1, 1), 10.0)
    insert_complete_itn_day(dt.date(2025, 1, 2), 20.0)
    insert_complete_itn_day(dt.date(2025, 2, 1), 30.0)

    refresh_itn_daily_observed_mv()

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
    insert_complete_itn_day(dt.date(2024, 1, 1), 10.0)
    insert_complete_itn_day(dt.date(2024, 12, 31), 20.0)
    insert_complete_itn_day(dt.date(2025, 1, 1), 30.0)

    refresh_itn_daily_observed_mv()

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
    insert_complete_itn_day(dt.date(2024, 1, 1), 10.0)
    insert_complete_itn_day(dt.date(2024, 2, 1), 100.0)
    insert_complete_itn_day(dt.date(2025, 1, 1), 20.0)
    insert_complete_itn_day(dt.date(2025, 2, 1), 200.0)

    refresh_itn_daily_observed_mv()

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
    insert_complete_itn_day(dt.date(2025, 1, 31), 31.0)
    insert_complete_itn_day(dt.date(2025, 2, 28), 28.0)
    insert_complete_itn_day(dt.date(2025, 2, 27), 999.0)
    refresh_itn_daily_observed_mv()

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
    insert_complete_itn_day(dt.date(2024, 2, 29), 29.0)
    insert_complete_itn_day(dt.date(2025, 2, 28), 28.0)
    insert_complete_itn_day(dt.date(2025, 2, 27), 999.0)

    refresh_itn_daily_observed_mv()

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


def test_fetch_observed_series_day_filters_target_dates():
    insert_complete_itn_day(dt.date(2025, 1, 1), 10.0)
    insert_complete_itn_day(dt.date(2025, 1, 2), 20.0)
    insert_complete_itn_day(dt.date(2025, 1, 3), 30.0)
    refresh_itn_daily_observed_mv()

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2025, 1, 1),
            date_end=dt.date(2025, 1, 3),
            granularity="day",
            slice_type="full",
            target_dates=(dt.date(2025, 1, 1), dt.date(2025, 1, 3)),
        )
    )

    assert [(p.date, p.temperature) for p in result] == [
        (dt.date(2025, 1, 1), pytest.approx(10.0)),
        (dt.date(2025, 1, 3), pytest.approx(30.0)),
    ]


def test_fetch_observed_series_ignores_target_dates_outside_range():
    insert_complete_itn_day(dt.date(2025, 1, 1), 10.0)
    insert_complete_itn_day(dt.date(2025, 1, 2), 20.0)
    refresh_itn_daily_observed_mv()

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2025, 1, 1),
            date_end=dt.date(2025, 1, 1),
            granularity="day",
            slice_type="full",
            target_dates=(dt.date(2025, 1, 2),),
        )
    )

    assert result == []


@pytest.mark.django_db
def test_fetch_observed_series_year_month_of_year_filters_month_even_with_target_dates():
    insert_complete_itn_day(dt.date(2024, 1, 1), 10.0)
    insert_complete_itn_day(dt.date(2024, 2, 1), 100.0)
    insert_complete_itn_day(dt.date(2025, 1, 1), 20.0)
    insert_complete_itn_day(dt.date(2025, 2, 1), 200.0)
    refresh_itn_daily_observed_mv()

    ds = TimescaleNationalIndicatorObservedDataSource()

    result = ds.fetch_observed_series(
        ObservedSeriesQuery(
            date_start=dt.date(2024, 1, 1),
            date_end=dt.date(2025, 2, 28),
            granularity="year",
            slice_type="month_of_year",
            month_of_year=1,
            target_dates=(
                dt.date(2024, 1, 1),
                dt.date(2024, 2, 1),
                dt.date(2025, 1, 1),
                dt.date(2025, 2, 1),
            ),
        )
    )

    assert [(p.date, p.temperature) for p in result] == [
        (dt.date(2024, 1, 1), pytest.approx(10.0)),
        (dt.date(2025, 1, 1), pytest.approx(20.0)),
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
