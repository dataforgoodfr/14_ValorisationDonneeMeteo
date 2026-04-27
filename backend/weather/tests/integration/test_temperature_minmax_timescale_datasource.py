from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import TimescaleTemperatureMinMaxDataSource
from weather.services.temperature_minmax.types import MinMaxGraphQuery
from weather.tests.conftest import insert_quotidienne
from weather.tests.helpers.stations import insert_station


@pytest.mark.django_db
def test_fetch_daily_series_happy_path():
    station_code = "07149001"

    insert_station(
        station_code, "Station Lyon", departement=69, lat=45.7, lon=4.8, alt=200.0
    )

    insert_quotidienne(dt.date(2024, 1, 1), station_code, tn=-2.0, tx=8.0)
    insert_quotidienne(dt.date(2024, 1, 2), station_code, tn=-1.0, tx=9.5)

    ds = TimescaleTemperatureMinMaxDataSource()

    query = MinMaxGraphQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        granularity="day",
        station_ids=(station_code,),
    )

    result = ds.fetch_daily_series(query)

    assert len(result) == 1
    s = result[0]
    assert s.station_id.strip() == station_code
    assert s.station_name == "Station Lyon"
    assert len(s.points) == 2
    assert s.points[0].date == dt.date(2024, 1, 1)
    assert s.points[0].tmin == pytest.approx(-2.0)
    assert s.points[0].tmax == pytest.approx(8.0)
    assert s.points[1].date == dt.date(2024, 1, 2)
    assert s.points[1].tmin == pytest.approx(-1.0)
    assert s.points[1].tmax == pytest.approx(9.5)


@pytest.mark.django_db
def test_fetch_daily_series_filters_by_department():
    s1 = "07149001"
    s2 = "07500001"

    insert_station(s1, "Station Lyon", departement=69, lat=45.7, lon=4.8, alt=200.0)
    insert_station(s2, "Station Paris", departement=75, lat=48.8, lon=2.3, alt=35.0)

    insert_quotidienne(dt.date(2024, 6, 1), s1, tn=14.0, tx=27.0)
    insert_quotidienne(dt.date(2024, 6, 1), s2, tn=16.0, tx=25.0)

    ds = TimescaleTemperatureMinMaxDataSource()

    query = MinMaxGraphQuery(
        date_start=dt.date(2024, 6, 1),
        date_end=dt.date(2024, 6, 1),
        granularity="day",
        departments=("69",),
    )

    result = ds.fetch_daily_series(query)

    assert len(result) == 1
    assert result[0].station_id.strip() == s1


@pytest.mark.django_db
def test_fetch_daily_series_returns_empty_when_no_match():
    station_code = "07149001"

    insert_station(station_code, "Station Lyon", departement=69)
    insert_quotidienne(dt.date(2024, 1, 1), station_code, tn=0.0, tx=10.0)

    ds = TimescaleTemperatureMinMaxDataSource()

    query = MinMaxGraphQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        granularity="day",
        station_ids=("99999999",),
    )

    result = ds.fetch_daily_series(query)

    assert result == []


@pytest.mark.django_db
def test_fetch_national_daily_series_happy_path():
    s1 = "07149001"
    s2 = "07500001"

    insert_station(s1, "Station A", departement=69)
    insert_station(s2, "Station B", departement=75)

    insert_quotidienne(dt.date(2024, 3, 1), s1, tn=4.0, tx=16.0)
    insert_quotidienne(dt.date(2024, 3, 1), s2, tn=6.0, tx=18.0)

    ds = TimescaleTemperatureMinMaxDataSource()

    query = MinMaxGraphQuery(
        date_start=dt.date(2024, 3, 1),
        date_end=dt.date(2024, 3, 1),
        granularity="day",
    )

    result = ds.fetch_national_daily_series(query)

    assert len(result) == 1
    assert result[0].date == dt.date(2024, 3, 1)
    assert result[0].tmin == pytest.approx(5.0)
    assert result[0].tmax == pytest.approx(17.0)
