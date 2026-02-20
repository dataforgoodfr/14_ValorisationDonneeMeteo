from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import (
    TimescaleNationalIndicatorDailyDataSource,
)
from weather.factories.weather import QuotidienneFactory
from weather.models import Station
from weather.services.national_indicator.stations import (
    ITN_ALWAYS_STATION_CODES,
    REIMS_COURCY,
    REIMS_PRUNAY,
    REIMS_SWITCH_DATE,
    expected_reims_code,
)


def make_station(code: str) -> Station:
    return Station.objects.create(
        code=code,
        nom=f"ITN {code}",
        lat=1.0,
        lon=1.0,
        alt=1.0,
        departement=0,
        type_poste=1,
        poste_public=True,
        poste_ouvert=True,
        frequence="horaire",
    )


@pytest.fixture()
def itn_stations(db) -> dict[str, Station]:
    # 29 always + 2 Reims
    codes = set(ITN_ALWAYS_STATION_CODES) | {REIMS_COURCY, REIMS_PRUNAY}
    return {code: make_station(code) for code in codes}


def mk_day(
    itn_stations: dict[str, Station],
    day: dt.date,
    *,
    always_val: float = 10.0,
    reims_val: float = 20.0,
    incomplete: bool = False,
) -> None:
    always_codes = list(ITN_ALWAYS_STATION_CODES)
    if incomplete:
        always_codes = always_codes[:-1]  # manque 1 always => drop

    for code in always_codes:
        QuotidienneFactory(station=itn_stations[code], date=day, tntxm=always_val)

    reims_code = expected_reims_code(day)
    QuotidienneFactory(station=itn_stations[reims_code], date=day, tntxm=reims_val)


@pytest.mark.django_db
def test_fetch_daily_series_happy_path_one_day_baseline_mean_equals_temperature(
    itn_stations,
):
    day = dt.date(2025, 1, 1)
    mk_day(itn_stations, day, always_val=10.0, reims_val=40.0)

    ds = TimescaleNationalIndicatorDailyDataSource()
    series = ds.fetch_daily_series(date_start=day, date_end=day)

    assert len(series) == 1
    p = series[0]
    assert p.date == day
    assert p.temperature == (29 * 10.0 + 40.0) / 30.0


@pytest.mark.django_db
def test_fetch_daily_series_drop_if_incomplete_day(itn_stations):
    day = dt.date(2025, 1, 1)
    mk_day(itn_stations, day, incomplete=True)

    ds = TimescaleNationalIndicatorDailyDataSource()
    series = ds.fetch_daily_series(date_start=day, date_end=day)

    assert series == []


@pytest.mark.django_db
def test_fetch_daily_series_accepts_double_reims_and_uses_expected(itn_stations):
    day = REIMS_SWITCH_DATE  # 2012-05-08 => Prunay attendue

    # 29 always
    for code in ITN_ALWAYS_STATION_CODES:
        QuotidienneFactory(station=itn_stations[code], date=day, tntxm=10.0)

    # Les deux Reims le même jour (Courcy doit être ignorée)
    QuotidienneFactory(station=itn_stations[REIMS_PRUNAY], date=day, tntxm=30.0)
    QuotidienneFactory(station=itn_stations[REIMS_COURCY], date=day, tntxm=999.0)

    ds = TimescaleNationalIndicatorDailyDataSource()
    series = ds.fetch_daily_series(date_start=day, date_end=day)

    assert len(series) == 1
    assert series[0].temperature == (29 * 10.0 + 30.0) / 30.0


@pytest.mark.django_db
def test_fetch_daily_series_multiple_days_keeps_only_valid_days_sorted(itn_stations):
    day1 = dt.date(2025, 1, 1)
    day2 = dt.date(2025, 1, 2)
    day3 = dt.date(2025, 1, 3)

    mk_day(itn_stations, day1, always_val=10.0, reims_val=20.0)
    mk_day(itn_stations, day2, incomplete=True)  # drop
    mk_day(itn_stations, day3, always_val=10.0, reims_val=40.0)

    ds = TimescaleNationalIndicatorDailyDataSource()
    series = ds.fetch_daily_series(date_start=day1, date_end=day3)

    assert [p.date for p in series] == [day1, day3]
    assert series[0].temperature == (29 * 10.0 + 20.0) / 30.0
    assert series[1].temperature == (29 * 10.0 + 40.0) / 30.0
