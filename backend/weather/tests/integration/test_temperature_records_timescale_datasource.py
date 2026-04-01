from __future__ import annotations

import datetime as dt

import pytest
from django.db import connection

from weather.data_sources.timescale import (
    TimescaleTemperatureRecordsDataSource,
)
from weather.services.temperature_records.types import TemperatureRecordsRequest

# =========================
# Helpers SQL
# =========================


def insert_station(code: str, name: str = "Station test", department: int = 1) -> None:
    now = dt.datetime.now()

    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Station"
                ("createdAt", "updatedAt", "id", "nom",
                 "departement", "frequence",
                 "posteOuvert", "typePoste",
                 "lon", "lat", "alt", "postePublic")
            VALUES
                (%(created)s, %(updated)s, %(id)s, %(name)s,
                 %(dept)s, 'horaire',
                 '1', 1,
                 0.0, 0.0, 0.0, '1')
            ON CONFLICT ("id", "frequence") DO UPDATE SET "nom" = EXCLUDED."nom"
            """,
            {
                "created": now,
                "updated": now,
                "id": code,
                "name": name,
                "dept": department,
            },
        )


def insert_quotidienne_full(
    day: dt.date,
    code: str,
    *,
    tx: float | None = None,
    tn: float | None = None,
) -> None:
    """Insert a Quotidienne row with TX and TN columns (not just TNTXM)."""
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Quotidienne"
                ("NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ", "TX", "TN", "TNTXM")
            VALUES
                (%(code)s, %(name)s, 0, 0, 0, %(day)s, %(tx)s, %(tn)s, %(tntxm)s)
            ON CONFLICT ("NUM_POSTE", "AAAAMMJJ")
            DO UPDATE SET "TX" = EXCLUDED."TX", "TN" = EXCLUDED."TN", "TNTXM" = EXCLUDED."TNTXM"
            """,
            {
                "code": code,
                "name": f"ST {code}",
                "day": day,
                "tx": tx,
                "tn": tn,
                "tntxm": ((tx or 0) + (tn or 0)) / 2 if tx and tn else None,
            },
        )


# =========================
# Tests
# =========================


@pytest.mark.django_db
def test_fetch_records_hot_month_happy_path():
    station_code = "99001001"

    insert_station(station_code, "Station Records Test", department=99)

    # Insert TX data for July across several years
    # 2003: 38.0 → premier record (prev_max=NULL)
    # 2019: 42.6 → 42.6 > 38.0 → record progressif
    # 2020: 35.0 → 35.0 < 42.6 → pas un record
    insert_quotidienne_full(dt.date(2003, 7, 15), station_code, tx=38.0, tn=20.0)
    insert_quotidienne_full(dt.date(2019, 7, 25), station_code, tx=42.6, tn=22.0)
    insert_quotidienne_full(dt.date(2020, 7, 10), station_code, tx=35.0, tn=19.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="month", type_records="hot", month=7)
    result = ds.fetch_records(req)

    station_entries = [e for e in result if e.station_id.strip() == station_code]
    # 2 records progressifs : 38.0 (2003) et 42.6 (2019)
    assert len(station_entries) == 2

    values = [e.record_value for e in station_entries]
    assert values == sorted(
        values
    ), "Les valeurs doivent être croissantes dans le temps"
    assert station_entries[-1].record_value == 42.6
    assert station_entries[-1].record_date == dt.date(2019, 7, 25)
    assert station_entries[0].station_name == "Station Records Test"
    assert station_entries[0].department == "99"


@pytest.mark.django_db
def test_fetch_records_cold_month_happy_path():
    station_code = "99002001"

    insert_station(station_code, "Station Cold Test", department=99)

    insert_quotidienne_full(dt.date(1985, 1, 16), station_code, tx=0.0, tn=-20.5)
    insert_quotidienne_full(dt.date(2010, 1, 7), station_code, tx=2.0, tn=-10.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="month", type_records="cold", month=1)
    result = ds.fetch_records(req)

    station_entries = [e for e in result if e.station_id.strip() == station_code]
    assert len(station_entries) == 1

    entry = station_entries[0]
    assert entry.record_value == -20.5
    assert entry.record_date == dt.date(1985, 1, 16)


@pytest.mark.django_db
def test_fetch_records_season_aggregates_across_months():
    station_code = "99003001"

    insert_station(station_code, "Station Season Test", department=99)

    # Summer = months 6, 7, 8
    # Ordre chronologique :
    # 2003-08-12: 40.0 → premier record estival
    # 2019-06-28: 44.0 → 44.0 > 40.0 → record progressif
    # 2019-07-25: 42.6 → 42.6 < 44.0 → pas un record
    insert_quotidienne_full(dt.date(2003, 8, 12), station_code, tx=40.0, tn=21.0)
    insert_quotidienne_full(dt.date(2019, 6, 28), station_code, tx=44.0, tn=25.0)
    insert_quotidienne_full(dt.date(2019, 7, 25), station_code, tx=42.6, tn=22.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="season", type_records="hot", season="summer"
    )
    result = ds.fetch_records(req)

    station_entries = [e for e in result if e.station_id.strip() == station_code]
    # 2 records progressifs : 40.0 (2003-08) et 44.0 (2019-06)
    assert len(station_entries) == 2

    values = [e.record_value for e in station_entries]
    assert values == sorted(
        values
    ), "Les valeurs doivent être croissantes dans le temps"
    assert station_entries[-1].record_value == 44.0


@pytest.mark.django_db
def test_fetch_records_all_time_returns_entries():
    station_code = "99004001"

    insert_station(station_code, "Station All Time", department=99)

    # Ordre chronologique :
    # 1985-01-16: tx=0.0 → premier record all-time
    # 2019-07-25: tx=42.6 → 42.6 > 0.0 → record progressif
    insert_quotidienne_full(dt.date(1985, 1, 16), station_code, tx=0.0, tn=-20.5)
    insert_quotidienne_full(dt.date(2019, 7, 25), station_code, tx=42.6, tn=22.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    station_entries = [e for e in result if e.station_id.strip() == station_code]
    # 2 records progressifs : 0.0 (1985) et 42.6 (2019)
    assert len(station_entries) == 2
    assert station_entries[-1].record_value == 42.6


@pytest.mark.django_db
def test_fetch_records_returns_correct_types():
    station_code = "99005001"

    insert_station(station_code, "Station Types Test", department=99)
    insert_quotidienne_full(dt.date(2019, 7, 25), station_code, tx=42.6, tn=22.0)

    ds = TimescaleTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    station_entries = [e for e in result if e.station_id.strip() == station_code]
    assert len(station_entries) >= 1

    entry = station_entries[0]
    assert isinstance(entry.station_id, str)
    assert isinstance(entry.station_name, str)
    assert isinstance(entry.department, str)
    assert isinstance(entry.record_value, float)
    assert isinstance(entry.record_date, dt.date)
