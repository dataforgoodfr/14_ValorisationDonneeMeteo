from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import (
    MaterializedTemperatureRecordsDataSource,
    TimescaleTemperatureRecordsDataSource,
)
from weather.services.temperature_records.types import TemperatureRecordsRequest
from weather.tests.conftest import insert_mv_record, insert_quotidienne
from weather.tests.helpers.stations import insert_station

# =========================
# Tests
# =========================


@pytest.mark.django_db
def test_fetch_records_hot_month_happy_path():
    station_code = "95001001"

    insert_station(
        station_code,
        "Station Records Test",
        departement=95,
        lat=48.0,
        lon=2.0,
        alt=100.0,
    )

    # Insert TX data for July across several years
    # 2003: 38.0 → premier record (prev_max=NULL)
    # 2019: 42.6 → 42.6 > 38.0 → record progressif
    # 2020: 35.0 → 35.0 < 42.6 → pas un record
    insert_quotidienne(dt.date(2003, 7, 15), station_code, tx=38.0, tn=20.0)
    insert_quotidienne(dt.date(2019, 7, 25), station_code, tx=42.6, tn=22.0)
    insert_quotidienne(dt.date(2020, 7, 10), station_code, tx=35.0, tn=19.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="month",
        type_records="hot",
        month=7,
        sort="record_value",
    )
    result = ds.fetch_records(req)

    station_entries = [
        e for e in result.entries if e.station_id.strip() == station_code
    ]
    # 2 records progressifs : 38.0 (2003) et 42.6 (2019)
    assert len(station_entries) == 2

    values = [e.record_value for e in station_entries]
    assert values == sorted(
        values
    ), "Les valeurs doivent être croissantes dans le temps"
    assert station_entries[-1].record_value == 42.6
    assert station_entries[-1].record_date == dt.date(2019, 7, 25)
    assert station_entries[0].station_name == "Station Records Test"
    assert station_entries[0].department == "95"
    assert station_entries[0].lat == 48.0
    assert station_entries[0].lon == 2.0
    assert station_entries[0].alt == 100.0


@pytest.mark.django_db
def test_fetch_records_cold_month_happy_path():
    station_code = "95002001"

    insert_station(
        station_code, "Station Cold Test", departement=95, lat=48.0, lon=2.0, alt=100.0
    )

    insert_quotidienne(dt.date(1985, 1, 16), station_code, tx=0.0, tn=-20.5)
    insert_quotidienne(dt.date(2010, 1, 7), station_code, tx=2.0, tn=-10.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="month", type_records="cold", month=1)
    result = ds.fetch_records(req)

    station_entries = [
        e for e in result.entries if e.station_id.strip() == station_code
    ]
    assert len(station_entries) == 1

    entry = station_entries[0]
    assert entry.record_value == -20.5
    assert entry.record_date == dt.date(1985, 1, 16)


@pytest.mark.django_db
def test_fetch_records_season_aggregates_across_months():
    station_code = "95003001"

    insert_station(
        station_code,
        "Station Season Test",
        departement=95,
        lat=48.0,
        lon=2.0,
        alt=100.0,
    )

    # Summer = months 6, 7, 8
    # Ordre chronologique :
    # 2003-08-12: 40.0 → premier record estival
    # 2019-06-28: 44.0 → 44.0 > 40.0 → record progressif
    # 2019-07-25: 42.6 → 42.6 < 44.0 → pas un record
    insert_quotidienne(dt.date(2003, 8, 12), station_code, tx=40.0, tn=21.0)
    insert_quotidienne(dt.date(2019, 6, 28), station_code, tx=44.0, tn=25.0)
    insert_quotidienne(dt.date(2019, 7, 25), station_code, tx=42.6, tn=22.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="season",
        type_records="hot",
        season="summer",
        sort="record_date",
    )
    result = ds.fetch_records(req)

    station_entries = [
        e for e in result.entries if e.station_id.strip() == station_code
    ]
    # 2 records progressifs : 40.0 (2003-08) et 44.0 (2019-06)
    assert len(station_entries) == 2

    values = [e.record_value for e in station_entries]
    assert values == sorted(
        values
    ), "Les valeurs doivent être croissantes dans le temps"
    assert station_entries[-1].record_value == 44.0


@pytest.mark.django_db
def test_fetch_records_all_time_returns_entries():
    station_code = "95004001"

    insert_station(
        station_code, "Station All Time", departement=95, lat=48.0, lon=2.0, alt=100.0
    )

    # Ordre chronologique :
    # 1985-01-16: tx=0.0 → premier record all-time
    # 2019-07-25: tx=42.6 → 42.6 > 0.0 → record progressif
    insert_quotidienne(dt.date(1985, 1, 16), station_code, tx=0.0, tn=-20.5)
    insert_quotidienne(dt.date(2019, 7, 25), station_code, tx=42.6, tn=22.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    station_entries = [
        e for e in result.entries if e.station_id.strip() == station_code
    ]
    # 2 records progressifs : 0.0 (1985) et 42.6 (2019)
    assert len(station_entries) == 2
    assert station_entries[-1].record_value == 42.6


@pytest.mark.django_db
def test_fetch_records_returns_correct_types():
    station_code = "95005001"

    insert_station(
        station_code, "Station Types Test", departement=95, lat=48.0, lon=2.0, alt=100.0
    )
    insert_quotidienne(dt.date(2019, 7, 25), station_code, tx=42.6, tn=22.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    station_entries = [
        e for e in result.entries if e.station_id.strip() == station_code
    ]
    assert len(station_entries) >= 1

    entry = station_entries[0]
    assert isinstance(entry.station_id, str)
    assert isinstance(entry.station_name, str)
    assert isinstance(entry.department, str)
    assert isinstance(entry.record_value, float)
    assert isinstance(entry.record_date, dt.date)
    assert isinstance(entry.lat, float)
    assert isinstance(entry.lon, float)
    assert isinstance(entry.alt, float)


@pytest.mark.django_db
def test_fetch_records_pagination_logic():
    station_code = "95006001"
    insert_station(station_code, "Station Pagination", departement=95)

    insert_quotidienne(dt.date(2000, 1, 1), station_code, tx=10.0, tn=0.0)
    insert_quotidienne(dt.date(2001, 1, 1), station_code, tx=20.0, tn=0.0)
    insert_quotidienne(dt.date(2002, 1, 1), station_code, tx=30.0, tn=0.0)

    ds = TimescaleTemperatureRecordsDataSource()

    req = TemperatureRecordsRequest(
        period_type="all_time", type_records="hot", page=1, page_size=2
    )
    result = ds.fetch_records(req)

    assert len(result.entries) == 2
    assert result.pagination.total_count >= 3
    assert result.pagination.page == 1
    assert result.pagination.total_pages >= 2

    req_page2 = TemperatureRecordsRequest(
        period_type="all_time", type_records="hot", page=2, page_size=2
    )
    result2 = ds.fetch_records(req_page2)
    assert len(result2.entries) == 1


@pytest.mark.django_db
def test_fetch_records_pagination_limit_and_offset():
    """Teste que la pagination (page/page_size) fonctionne comme limit/offset."""
    station_code = "95008001"
    insert_station(station_code, "Station Pagination", departement=95)

    #  insert 3 records
    insert_quotidienne(dt.date(2000, 1, 1), station_code, tx=10.0, tn=0.0)
    insert_quotidienne(dt.date(2010, 1, 1), station_code, tx=20.0, tn=0.0)
    insert_quotidienne(dt.date(2020, 1, 1), station_code, tx=30.0, tn=0.0)

    ds = TimescaleTemperatureRecordsDataSource()

    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        page=2,  # Équivalent offset 1
        page_size=1,  # Équivalent limit 1
    )
    result = ds.fetch_records(req)

    assert result.pagination.total_count == 3
    assert len(result.entries) == 1

    assert result.entries[0].record_date == dt.date(2010, 1, 1)


@pytest.mark.django_db
def test_fetch_records_sorting_by_value_desc():
    """Teste le tri par valeur décroissante (-record_value)."""
    s1 = "99009001"
    s2 = "99009002"
    insert_station(s1, "Station A", departement=11)
    insert_station(s2, "Station B", departement=22)

    insert_quotidienne(dt.date(2020, 1, 1), s1, tx=15.0, tn=0.0)
    insert_quotidienne(dt.date(2020, 1, 1), s2, tx=35.0, tn=0.0)

    ds = TimescaleTemperatureRecordsDataSource()

    req = TemperatureRecordsRequest(
        period_type="all_time", type_records="hot", sort="-record_value"
    )
    result = ds.fetch_records(req)

    assert len(result.entries) >= 2

    assert result.entries[0].record_value == 35.0
    assert result.entries[1].record_value == 15.0


@pytest.mark.django_db
def test_fetch_records_sorting_by_station_name_desc():
    """Teste le tri inversé sur un champ texte (important pour valider ta logique chr(255-ord))."""
    s1 = "55001001"
    s2 = "62906001"
    insert_station(s1, "ABAINVILLE", departement=55)
    insert_station(s2, "ZUTKERQUE", departement=62)

    insert_quotidienne(dt.date(2020, 1, 1), s1, tx=20.0, tn=0.0)
    insert_quotidienne(dt.date(2020, 1, 1), s2, tx=20.0, tn=0.0)

    ds = TimescaleTemperatureRecordsDataSource()

    req = TemperatureRecordsRequest(
        period_type="all_time", type_records="hot", sort="-station_name"
    )
    result = ds.fetch_records(req)

    names = [e.station_name for e in result.entries if e.station_id in [s1, s2]]
    assert names == ["ZUTKERQUE", "ABAINVILLE"]


@pytest.mark.django_db
def test_fetch_records_all_months_returns_records_for_each_month():
    """period_type='month' sans month → retourne les records de tous les mois via la MV."""
    station_code = "95011001"

    insert_station(
        station_code,
        "Station All Months",
        departement=95,
        lat=48.0,
        lon=2.0,
        alt=100.0,
    )

    insert_mv_record(
        station_code,
        "Station All Months",
        "month",
        "7",
        "TX",
        40.0,
        dt.date(2003, 7, 15),
    )
    insert_mv_record(
        station_code,
        "Station All Months",
        "month",
        "8",
        "TX",
        38.0,
        dt.date(2001, 8, 10),
    )
    insert_mv_record(
        station_code,
        "Station All Months",
        "month",
        "1",
        "TX",
        5.0,
        dt.date(1990, 1, 20),
    )

    ds = MaterializedTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="month", type_records="hot", month=None)
    result = ds.fetch_records(req)

    station_entries = [e for e in result if e.station_id.strip() == station_code]
    values = {e.record_value for e in station_entries}
    assert 40.0 in values
    assert 38.0 in values
    assert 5.0 in values


@pytest.mark.django_db
def test_fetch_records_all_seasons_returns_records_for_each_season():
    """period_type='season' sans season → retourne les records de toutes les saisons via la MV."""
    station_code = "95012001"

    insert_station(
        station_code,
        "Station All Seasons",
        departement=95,
        lat=48.0,
        lon=2.0,
        alt=100.0,
    )

    insert_mv_record(
        station_code,
        "Station All Seasons",
        "season",
        "summer",
        "TX",
        42.0,
        dt.date(2003, 8, 12),
    )
    insert_mv_record(
        station_code,
        "Station All Seasons",
        "season",
        "winter",
        "TX",
        8.0,
        dt.date(2010, 1, 5),
    )

    ds = MaterializedTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="season", type_records="hot", season=None
    )
    result = ds.fetch_records(req)

    station_entries = [e for e in result if e.station_id.strip() == station_code]
    values = {e.record_value for e in station_entries}
    assert 42.0 in values
    assert 8.0 in values


@pytest.mark.django_db
def test_fetch_records_date_filter_excludes_outside_range():
    """date_start/date_end filtre les records dont record_date est hors fenêtre."""
    station_code = "95013001"

    insert_station(
        station_code,
        "Station Date Filter",
        departement=95,
        lat=48.0,
        lon=2.0,
        alt=100.0,
    )

    # Record dans la fenêtre (2024-06-15)
    insert_mv_record(
        station_code,
        "Station Date Filter",
        "month",
        "6",
        "TX",
        38.0,
        dt.date(2024, 6, 15),
    )
    # Record hors fenêtre (2003-07-15)
    insert_mv_record(
        station_code,
        "Station Date Filter",
        "month",
        "7",
        "TX",
        42.0,
        dt.date(2003, 7, 15),
    )

    ds = MaterializedTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="month",
        type_records="hot",
        month=None,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 12, 31),
    )
    result = ds.fetch_records(req)

    station_entries = [e for e in result if e.station_id.strip() == station_code]
    values = {e.record_value for e in station_entries}
    assert 38.0 in values
    assert 42.0 not in values
