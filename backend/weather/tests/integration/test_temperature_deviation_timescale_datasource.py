from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import (
    TimescaleTemperatureDeviationDailyDataSource,
)
from weather.services.temperature_deviation.types import (
    DailyDeviationSeriesQuery,
    TemperatureDeviationOverviewQuery,
)
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


@pytest.mark.django_db
def test_fetch_station_overview_happy_path():
    station_code = "01269001"

    insert_station(
        station_code,
        "Station 01269001",
        departement=13,
        lat=43.3,
        lon=5.4,
        alt=120.0,
    )

    insert_station_daily_baseline(station_code, 1, 1, 10.0)
    insert_station_daily_baseline(station_code, 1, 2, 12.0)

    insert_quotidienne(dt.date(2024, 1, 1), station_code, 14.0)
    insert_quotidienne(dt.date(2024, 1, 2), station_code, 13.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        offset=0,
        limit=10,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 1
    assert len(result.stations) == 1

    station = result.stations[0]

    assert station.station_id == station_code
    assert station.station_name == "Station 01269001"
    assert station.lat == pytest.approx(43.3)
    assert station.lon == pytest.approx(5.4)
    assert station.department == "13"
    assert station.alt == pytest.approx(120.0)
    assert station.region == "Provence-Alpes-Côte d'Azur"

    assert station.temperature_mean == pytest.approx((14.0 + 13.0) / 2)
    assert station.baseline_mean == pytest.approx((10.0 + 12.0) / 2)
    assert station.deviation == pytest.approx(2.5)


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_department():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1", departement=13, lat=43.3, lon=5.4, alt=50.0)
    insert_station(s2, "Station 2", departement=75, lat=48.8, lon=2.3, alt=60.0)

    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 10.0)

    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 12.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        departments=("13",),
        offset=0,
        limit=10,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 1
    assert len(result.stations) == 1
    assert result.stations[0].station_id == s1
    assert result.stations[0].department == "13"


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_region():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1", departement=13, lat=43.3, lon=5.4, alt=50.0)
    insert_station(s2, "Station 2", departement=75, lat=48.8, lon=2.3, alt=60.0)

    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 10.0)

    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 12.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        regions=("Île-de-France",),
        offset=0,
        limit=10,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 1
    assert len(result.stations) == 1
    assert result.stations[0].station_id == s2
    assert result.stations[0].region == "Île-de-France"


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_altitude():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1", departement=13, lat=43.3, lon=5.4, alt=50.0)
    insert_station(s2, "Station 2", departement=75, lat=48.8, lon=2.3, alt=200.0)

    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 10.0)

    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 12.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        alt_min=100.0,
        offset=0,
        limit=10,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 1
    assert len(result.stations) == 1
    assert result.stations[0].station_id == s2
    assert result.stations[0].alt == pytest.approx(200.0)


@pytest.mark.django_db
def test_fetch_station_overview_applies_limit_and_offset():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station A", departement=13, lat=43.3, lon=5.4, alt=50.0)
    insert_station(s2, "Station B", departement=75, lat=48.8, lon=2.3, alt=60.0)

    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 10.0)

    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 11.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    result = ds.fetch_station_overview(
        TemperatureDeviationOverviewQuery(
            date_start=dt.date(2024, 1, 1),
            date_end=dt.date(2024, 1, 1),
            ordering="station_name",
            offset=1,
            limit=1,
        )
    )

    assert result.pagination.total_count == 2
    assert result.pagination.offset == 1
    assert result.pagination.limit == 1
    assert len(result.stations) == 1
    assert result.stations[0].station_name == "Station B"


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_station_ids():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1", departement=13, lat=43.3, lon=5.4, alt=50.0)
    insert_station(s2, "Station 2", departement=75, lat=48.8, lon=2.3, alt=60.0)

    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 10.0)

    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 12.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        station_ids=(s2,),
        offset=0,
        limit=10,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 1
    assert len(result.stations) == 1
    assert result.stations[0].station_id == s2


@pytest.mark.django_db
def test_fetch_station_overview_combines_station_ids_and_department_filters():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1", departement=13, lat=43.3, lon=5.4, alt=50.0)
    insert_station(s2, "Station 2", departement=75, lat=48.8, lon=2.3, alt=60.0)

    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 10.0)

    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 12.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        station_ids=(s1, s2),
        departments=("13",),
        offset=0,
        limit=10,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 1
    assert len(result.stations) == 1
    assert result.stations[0].station_id == s1


@pytest.mark.django_db
def test_fetch_station_overview_orders_by_department():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1", departement=75, lat=48.8, lon=2.3, alt=60.0)
    insert_station(s2, "Station 2", departement=13, lat=43.3, lon=5.4, alt=50.0)

    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 10.0)

    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 12.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        ordering="department",
        offset=0,
        limit=10,
    )

    result = ds.fetch_station_overview(query)

    assert len(result.stations) == 2
    assert [s.department for s in result.stations] == ["13", "75"]


@pytest.mark.django_db
def test_fetch_station_overview_orders_by_region():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1", departement=75, lat=48.8, lon=2.3, alt=60.0)
    insert_station(s2, "Station 2", departement=13, lat=43.3, lon=5.4, alt=50.0)

    insert_station_daily_baseline(s1, 1, 1, 10.0)
    insert_station_daily_baseline(s2, 1, 1, 10.0)

    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 12.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        ordering="region",
        offset=0,
        limit=10,
    )

    result = ds.fetch_station_overview(query)

    assert len(result.stations) == 2
    assert [s.region for s in result.stations] == [
        "Provence-Alpes-Côte d'Azur",
        "Île-de-France",
    ]
