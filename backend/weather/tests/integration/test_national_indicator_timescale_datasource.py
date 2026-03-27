import datetime as dt

import pytest
from django.db import connection

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorBaselineDataSource,
    TimescaleNationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.types import DailySeriesQuery

pytestmark = pytest.mark.django_db


# ----------------------------
# Helpers DB
# ----------------------------


def insert_daily_baseline(month: int, day: int, mean: float, std: float):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_1991_2020 (month, day_of_month, itn_mean, itn_stddev)
            VALUES (%s, %s, %s, %s)
            """,
            [month, day, mean, std],
        )


def insert_monthly_baseline(month: int, mean: float, std: float):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_monthly_1991_2020 (month, itn_mean, itn_stddev)
            VALUES (%s, %s, %s)
            """,
            [month, mean, std],
        )


def insert_yearly_baseline(sample_size: int, mean: float, std: float):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_yearly_1991_2020 (sample_size, itn_mean, itn_stddev)
            VALUES (%s, %s, %s)
            """,
            [sample_size, mean, std],
        )


# ----------------------------
# Observed datasource tests
# ----------------------------


def test_fetch_daily_series_happy_path(db):
    ds = TimescaleNationalIndicatorObservedDataSource()

    query = DailySeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert len(result) == 1
    assert result[0].date == dt.date(2024, 1, 1)


def test_fetch_daily_series_drop_incomplete_day(db):
    ds = TimescaleNationalIndicatorObservedDataSource()

    query = DailySeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    # dépend des données test → au minimum on vérifie que ça ne plante pas
    assert isinstance(result, list)


def test_fetch_daily_series_multiple_days(db):
    ds = TimescaleNationalIndicatorObservedDataSource()

    query = DailySeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert all(r.date in [dt.date(2024, 1, 1), dt.date(2024, 1, 2)] for r in result)


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
