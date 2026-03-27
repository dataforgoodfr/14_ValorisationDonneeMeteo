import datetime as dt
from collections.abc import Callable

import pytest
from django.db import connection

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorBaselineDataSource,
    TimescaleNationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.stations import (
    ITN_ALWAYS_STATION_CODES,
    REIMS_COURCY,
    REIMS_PRUNAY,
    expected_reims_code,
)
from weather.services.national_indicator.types import DailySeriesQuery

pytestmark = pytest.mark.django_db


# ----------------------------
# Helpers DB
# ----------------------------


def insert_daily_baseline(
    month: int,
    day: int,
    mean: float,
    std: float,
    *,
    sample_size: int = 30,
    p20: float = 8.0,
    p80: float = 12.0,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_1991_2020
                (month, day_of_month, sample_size, itn_mean, itn_stddev, itn_p20, itn_p80)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            [month, day, sample_size, mean, std, p20, p80],
        )


def insert_monthly_baseline(
    month: int,
    mean: float,
    std: float,
    *,
    sample_size: int = 30,
    p20: float = 18.0,
    p80: float = 22.0,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_monthly_1991_2020
                (month, sample_size, itn_mean, itn_stddev, itn_p20, itn_p80)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            [month, sample_size, mean, std, p20, p80],
        )


def insert_yearly_baseline(
    sample_size: int,
    mean: float,
    std: float,
    *,
    p20: float = 28.0,
    p80: float = 32.0,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_yearly_1991_2020
                (sample_size, itn_mean, itn_stddev, itn_p20, itn_p80)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [sample_size, mean, std, p20, p80],
        )


def insert_quotidienne(day: dt.date, code: str, tntxm: float) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO public."Quotidienne"
              ("NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ", "TNTXM")
            VALUES
              (%s, %s, 0.0, 0.0, 0.0, %s, %s)
            ON CONFLICT ("NUM_POSTE", "AAAAMMJJ")
            DO UPDATE SET "TNTXM" = EXCLUDED."TNTXM"
            """,
            [code, f"ST {code}", day, tntxm],
        )


@pytest.fixture()
def seed_itn_day() -> Callable[..., None]:
    def _seed(
        day: dt.date,
        *,
        always_val: float = 10.0,
        reims_val: float = 20.0,
        incomplete: bool = False,
        include_both_reims: bool = False,
        other_reims_val: float = 30.0,
    ) -> None:
        always_codes = list(ITN_ALWAYS_STATION_CODES)

        if incomplete:
            always_codes = always_codes[:-1]

        for code in always_codes:
            insert_quotidienne(day, code, always_val)

        reims_expected = expected_reims_code(day)
        insert_quotidienne(day, reims_expected, reims_val)

        if include_both_reims:
            other = REIMS_PRUNAY if reims_expected == REIMS_COURCY else REIMS_COURCY
            insert_quotidienne(day, other, other_reims_val)

    return _seed


# ----------------------------
# Observed datasource tests
# ----------------------------
def test_fetch_daily_series_happy_path(
    seed_itn_day: Callable[..., None],
):
    day = dt.date(2025, 1, 1)
    seed_itn_day(day)

    ds = TimescaleNationalIndicatorObservedDataSource()
    query = DailySeriesQuery(
        date_start=day,
        date_end=day,
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert len(result) == 1
    assert result[0].date == day
    assert result[0].temperature == pytest.approx((29 * 10.0 + 20.0) / 30.0)


def test_fetch_daily_series_drop_incomplete_day(
    seed_itn_day: Callable[..., None],
):
    day = dt.date(2025, 1, 1)
    seed_itn_day(day, incomplete=True)

    ds = TimescaleNationalIndicatorObservedDataSource()
    query = DailySeriesQuery(
        date_start=day,
        date_end=day,
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert result == []


def test_fetch_daily_series_multiple_days(
    seed_itn_day: Callable[..., None],
):
    d1 = dt.date(2025, 1, 1)
    d2 = dt.date(2025, 1, 2)
    seed_itn_day(d1)
    seed_itn_day(d2)

    ds = TimescaleNationalIndicatorObservedDataSource()
    query = DailySeriesQuery(
        date_start=d1,
        date_end=d2,
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert len(result) == 2
    assert [p.date for p in result] == [d1, d2]


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
