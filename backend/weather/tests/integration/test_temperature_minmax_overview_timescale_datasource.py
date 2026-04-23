from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import (
    TimescaleTemperatureMinMaxOverviewDataSource,
)
from weather.services.temperature_minmax.types import MinMaxOverviewQuery
from weather.tests.conftest import insert_quotidienne
from weather.tests.helpers.stations import insert_station


def _query(**overrides) -> MinMaxOverviewQuery:
    params = {
        "date_start": dt.date(2024, 1, 1),
        "date_end": dt.date(2024, 12, 31),
    }
    params.update(overrides)
    return MinMaxOverviewQuery(**params)


@pytest.mark.django_db
def test_fetch_station_overview_happy_path():
    code = "07149001"
    insert_station(code, "Station Lyon", departement=69, lat=45.7, lon=4.8, alt=200.0)
    insert_quotidienne(dt.date(2024, 1, 1), code, tn=0.0, tx=10.0)
    insert_quotidienne(dt.date(2024, 1, 2), code, tn=2.0, tx=12.0)

    ds = TimescaleTemperatureMinMaxOverviewDataSource()

    result = ds.fetch_station_overview(_query(type="tmax"))

    assert result.pagination.total_count == 1
    assert len(result.stations) == 1
    s = result.stations[0]
    assert s.station_id == code
    assert s.station_name == "Station Lyon"
    assert s.textreme_mean == pytest.approx(11.0)
    assert s.tmean_mean == pytest.approx(6.0)
    assert s.alt == pytest.approx(200.0)
    assert s.department == "69"


@pytest.mark.django_db
def test_fetch_station_overview_type_tmin_uses_tmin_as_textreme():
    code = "07149001"
    insert_station(code, "Station Lyon", departement=69)
    insert_quotidienne(dt.date(2024, 1, 1), code, tn=0.0, tx=10.0)
    insert_quotidienne(dt.date(2024, 1, 2), code, tn=2.0, tx=12.0)

    ds = TimescaleTemperatureMinMaxOverviewDataSource()
    result = ds.fetch_station_overview(_query(type="tmin"))

    assert result.stations[0].textreme_mean == pytest.approx(1.0)


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_department():
    s1, s2 = "07149001", "07500001"
    insert_station(s1, "Lyon", departement=69)
    insert_station(s2, "Paris", departement=75)
    insert_quotidienne(dt.date(2024, 1, 1), s1, tn=5.0, tx=15.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, tn=3.0, tx=13.0)

    ds = TimescaleTemperatureMinMaxOverviewDataSource()
    result = ds.fetch_station_overview(_query(departments=("69",)))

    assert result.pagination.total_count == 1
    assert result.stations[0].station_id == s1


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_textreme_min():
    s1, s2 = "07149001", "07500001"
    insert_station(s1, "A", departement=69)
    insert_station(s2, "B", departement=75)
    insert_quotidienne(dt.date(2024, 1, 1), s1, tn=0.0, tx=10.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, tn=0.0, tx=30.0)

    ds = TimescaleTemperatureMinMaxOverviewDataSource()
    result = ds.fetch_station_overview(_query(type="tmax", textreme_min=20.0))

    assert result.pagination.total_count == 1
    assert result.stations[0].station_id == s2


@pytest.mark.django_db
def test_fetch_station_overview_orders_by_textreme_desc():
    s1, s2 = "07149001", "07500001"
    insert_station(s1, "A", departement=69)
    insert_station(s2, "B", departement=75)
    insert_quotidienne(dt.date(2024, 1, 1), s1, tn=0.0, tx=10.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, tn=0.0, tx=30.0)

    ds = TimescaleTemperatureMinMaxOverviewDataSource()
    result = ds.fetch_station_overview(_query(type="tmax", ordering="-textreme_mean"))

    assert [s.station_id for s in result.stations] == [s2, s1]


@pytest.mark.django_db
def test_fetch_station_overview_applies_limit_and_offset():
    s1, s2 = "07149001", "07500001"
    insert_station(s1, "Station A", departement=69)
    insert_station(s2, "Station B", departement=75)
    insert_quotidienne(dt.date(2024, 1, 1), s1, tn=0.0, tx=10.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, tn=0.0, tx=20.0)

    ds = TimescaleTemperatureMinMaxOverviewDataSource()
    result = ds.fetch_station_overview(
        _query(ordering="station_name", offset=1, limit=1)
    )

    assert result.pagination.total_count == 2
    assert result.pagination.offset == 1
    assert result.pagination.limit == 1
    assert len(result.stations) == 1
    assert result.stations[0].station_name == "Station B"
