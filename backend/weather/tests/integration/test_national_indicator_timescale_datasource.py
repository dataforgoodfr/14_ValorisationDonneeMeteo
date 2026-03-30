from __future__ import annotations

import datetime as dt

import pytest
from django.db import connection

from weather.data_sources.timescale import TimescaleNationalIndicatorDailyDataSource
from weather.services.national_indicator.stations import (
    ITN_ALWAYS_STATION_CODES,
    REIMS_COURCY,
    REIMS_PRUNAY,
    expected_reims_code,
)
from weather.services.national_indicator.types import DailySeriesQuery


def insert_quotidienne(day: dt.date, code: str, tntxm: float) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Quotidienne"
              ("NUM_POSTE","NOM_USUEL","LAT","LON","ALTI","AAAAMMJJ","TNTXM")
            VALUES
              (%(code)s, %(name)s, 0.0, 0.0, 0.0, %(day)s, %(tntxm)s)
            ON CONFLICT ("NUM_POSTE","AAAAMMJJ")
            DO UPDATE SET "TNTXM" = EXCLUDED."TNTXM"
            """,
            {
                "code": code,
                "name": f"ST {code}",
                "day": day,
                "tntxm": tntxm,
            },
        )


@pytest.fixture()
def seed_itn_day(db):
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


@pytest.mark.django_db
def test_fetch_daily_series_happy_path(seed_itn_day):
    day = dt.date(2025, 1, 1)
    seed_itn_day(day)

    ds = TimescaleNationalIndicatorDailyDataSource()

    query = DailySeriesQuery(
        date_start=day,
        date_end=day,
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert len(result) == 1
    assert result[0].date == day
    assert result[0].temperature == pytest.approx((29 * 10 + 20) / 30)


@pytest.mark.django_db
def test_fetch_daily_series_drop_incomplete_day(seed_itn_day):
    day = dt.date(2025, 1, 1)

    seed_itn_day(day, incomplete=True)

    ds = TimescaleNationalIndicatorDailyDataSource()

    query = DailySeriesQuery(
        date_start=day,
        date_end=day,
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert result == []


@pytest.mark.django_db
def test_fetch_daily_series_double_reims(seed_itn_day):
    day = dt.date(2025, 1, 1)

    seed_itn_day(day, include_both_reims=True)

    ds = TimescaleNationalIndicatorDailyDataSource()

    query = DailySeriesQuery(
        date_start=day,
        date_end=day,
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert len(result) == 1


@pytest.mark.django_db
def test_fetch_daily_series_multiple_days(seed_itn_day):
    d1 = dt.date(2025, 1, 1)
    d2 = dt.date(2025, 1, 2)

    seed_itn_day(d1)
    seed_itn_day(d2)

    ds = TimescaleNationalIndicatorDailyDataSource()

    query = DailySeriesQuery(
        date_start=d1,
        date_end=d2,
        target_dates=None,
    )

    result = ds.fetch_daily_series(query)

    assert len(result) == 2
