from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import (
    TimescaleTemperatureDeviationDailyDataSource,
)
from weather.services.temperature_deviation.types import DailyDeviationSeriesQuery
from weather.tests.helpers.itn import insert_complete_itn_day, insert_quotidienne
from weather.tests.helpers.stations import insert_station
from weather.tests.helpers.stations_baseline import insert_station_daily_baseline


@pytest.mark.django_db
def test_fetch_stations_daily_series_happy_path():
    station_code = "01269001"

    insert_station(station_code, "Station 01269001")

    # --- baseline (>= 24 années requises)
    insert_station_daily_baseline(station_code, 1, 1, 10.0)
    insert_station_daily_baseline(station_code, 1, 2, 12.0)

    # --- observations
    insert_quotidienne(dt.date(2024, 1, 1), station_code, 14.0)
    insert_quotidienne(dt.date(2024, 1, 2), station_code, 13.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        station_ids=(station_code,),
        include_national=False,
    )

    result = ds.fetch_stations_daily_series(query)

    assert len(result) == 1

    s = result[0]

    assert s.station_id == station_code
    assert s.station_name == "Station 01269001"

    assert [p.date for p in s.points] == [
        dt.date(2024, 1, 1),
        dt.date(2024, 1, 2),
    ]

    # valeurs observées
    assert s.points[0].temperature == 14.0
    assert s.points[1].temperature == 13.0

    # baseline issue de la MV
    assert s.points[0].baseline_mean == pytest.approx(10.0)
    assert s.points[1].baseline_mean == pytest.approx(12.0)


@pytest.mark.django_db
def test_fetch_stations_daily_series_filters_out_missing_baseline():
    station_code = "01269001"

    insert_station(station_code, "Station 01269001")

    insert_quotidienne(dt.date(2024, 1, 3), station_code, 15.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 3),
        date_end=dt.date(2024, 1, 3),
        station_ids=(station_code,),
        include_national=False,
    )

    result = ds.fetch_stations_daily_series(query)

    assert result == []


@pytest.mark.django_db
def test_fetch_stations_daily_series_multiple_stations():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1")
    insert_station(s2, "Station 2")

    # baseline pour les deux
    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 5.0)

    # observations
    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 6.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        station_ids=(s1, s2),
        include_national=False,
    )

    result = ds.fetch_stations_daily_series(query)

    assert len(result) == 2
    assert [s.station_id for s in result] == [s1, s2]


@pytest.mark.django_db
def test_fetch_national_observed_series_happy_path():
    day = dt.date(2024, 1, 1)

    insert_complete_itn_day(day, 10.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = DailyDeviationSeriesQuery(
        date_start=day,
        date_end=day,
        station_ids=(),
        include_national=True,
    )

    result = ds.fetch_national_observed_series(query)

    assert len(result) == 1
    assert result[0].date == day
    assert result[0].temperature == pytest.approx(10.0)
