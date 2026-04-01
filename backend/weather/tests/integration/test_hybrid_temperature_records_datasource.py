from __future__ import annotations

import datetime as dt
from unittest.mock import patch

import pytest
from django.db import connection

from weather.data_sources.timescale import HybridTemperatureRecordsDataSource
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


def insert_quotidienne(
    day: dt.date,
    code: str,
    *,
    tx: float | None = None,
    tn: float | None = None,
) -> None:
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


def insert_mv_record(
    station_code: str,
    station_name: str,
    period_type: str,
    period_value: str | None,
    record_type: str,
    value: float,
    date: dt.date,
    department: int = 75,
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_records_absolus
                (period_type, period_value, record_type,
                 station_code, station_name, department,
                 record_value, record_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                period_type,
                period_value,
                record_type,
                station_code,
                station_name,
                department,
                value,
                date,
            ],
        )


def set_cutoff(date: dt.date) -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_absolus_meta;")
        cur.execute(
            "INSERT INTO public.mv_records_absolus_meta (cutoff_date) VALUES (%s);",
            [date],
        )


def clear_mv() -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_absolus;")
        cur.execute("TRUNCATE public.mv_records_absolus_meta;")


# =========================
# Tests
# =========================


@pytest.mark.django_db
def test_no_cutoff_returns_mv_only():
    """Méta table vide → retourne uniquement les données MV, sans query à chaud."""
    code = "98001001"
    insert_station(code, "Station Hybrid 1", department=98)
    insert_mv_record(
        code, "Station Hybrid 1", "all_time", None, "TX", 38.0, dt.date(2003, 7, 15)
    )
    # Ne pas appeler set_cutoff → méta vide

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 38.0


@pytest.mark.django_db
def test_cutoff_future_no_new_data():
    """Cutoff = aujourd'hui, données Quotidienne avant cutoff → aucun ajout."""
    code = "98002001"
    insert_station(code, "Station Hybrid 2", department=98)
    insert_mv_record(
        code, "Station Hybrid 2", "all_time", None, "TX", 38.0, dt.date(2003, 7, 15)
    )
    set_cutoff(dt.date.today())

    # Donnée avant cutoff (2024)
    insert_quotidienne(dt.date(2024, 7, 1), code, tx=35.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 38.0


@pytest.mark.django_db
def test_new_hot_record_after_cutoff_is_added():
    """Record chaud battu après cutoff → ligne ajoutée dans les résultats."""
    code = "98003001"
    insert_station(code, "Station Hybrid 3", department=98)
    insert_mv_record(
        code, "Station Hybrid 3", "all_time", None, "TX", 38.0, dt.date(2003, 7, 15)
    )
    cutoff = dt.date(2025, 12, 31)
    set_cutoff(cutoff)

    insert_quotidienne(dt.date(2026, 7, 15), code, tx=45.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    values = [e.record_value for e in entries]
    assert 38.0 in values
    assert 45.0 in values
    assert entries[-1].record_date == dt.date(2026, 7, 15)


@pytest.mark.django_db
def test_value_below_seed_not_added():
    """Valeur après cutoff inférieure au seed → pas ajoutée."""
    code = "98004001"
    insert_station(code, "Station Hybrid 4", department=98)
    insert_mv_record(
        code, "Station Hybrid 4", "all_time", None, "TX", 42.0, dt.date(2019, 7, 25)
    )
    set_cutoff(dt.date(2025, 12, 31))

    insert_quotidienne(dt.date(2026, 7, 1), code, tx=39.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 42.0


@pytest.mark.django_db
def test_new_station_after_cutoff_gets_first_record():
    """Nouvelle station absente de la MV → son premier jour après cutoff = record."""
    code = "98005001"
    insert_station(code, "Station Hybrid 5", department=98)
    set_cutoff(dt.date(2025, 12, 31))

    insert_quotidienne(dt.date(2026, 3, 15), code, tx=22.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 22.0
    assert entries[0].record_date == dt.date(2026, 3, 15)


@pytest.mark.django_db
def test_new_cold_record_after_cutoff():
    """Record froid battu après cutoff → type_records='cold'."""
    code = "98006001"
    insert_station(code, "Station Hybrid 6", department=98)
    insert_mv_record(
        code, "Station Hybrid 6", "all_time", None, "TN", -20.0, dt.date(1985, 1, 16)
    )
    set_cutoff(dt.date(2025, 12, 31))

    insert_quotidienne(dt.date(2026, 1, 10), code, tn=-25.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="cold")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    values = [e.record_value for e in entries]
    assert -20.0 in values
    assert -25.0 in values


@pytest.mark.django_db
def test_cold_above_seed_not_added():
    """TN après cutoff supérieure (moins froid) au seed → pas ajoutée."""
    code = "98007001"
    insert_station(code, "Station Hybrid 7", department=98)
    insert_mv_record(
        code, "Station Hybrid 7", "all_time", None, "TN", -20.0, dt.date(1985, 1, 16)
    )
    set_cutoff(dt.date(2025, 12, 31))

    insert_quotidienne(dt.date(2026, 1, 5), code, tn=-15.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="cold")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == -20.0


@pytest.mark.django_db
def test_month_filter_respected():
    """Filtre period_type='month' : données hors mois ignorées dans le hot calc."""
    code = "98008001"
    insert_station(code, "Station Hybrid 8", department=98)
    insert_mv_record(
        code, "Station Hybrid 8", "month", "7", "TX", 38.0, dt.date(2003, 7, 15)
    )
    set_cutoff(dt.date(2025, 12, 31))

    # Donnée en août (hors mois 7)
    insert_quotidienne(dt.date(2026, 8, 10), code, tx=50.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="month", type_records="hot", month=7)
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 38.0


@pytest.mark.django_db
def test_season_filter_respected():
    """Filtre period_type='season' : données hors saison ignorées dans le hot calc."""
    code = "98009001"
    insert_station(code, "Station Hybrid 9", department=98)
    insert_mv_record(
        code, "Station Hybrid 9", "season", "summer", "TX", 40.0, dt.date(2003, 8, 12)
    )
    set_cutoff(dt.date(2025, 12, 31))

    # Donnée en janvier (hors été)
    insert_quotidienne(dt.date(2026, 1, 5), code, tx=50.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(
            period_type="season", type_records="hot", season="summer"
        )
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 40.0


@pytest.mark.django_db
def test_meta_table_absent_falls_back_to_mv():
    """Erreur DB sur la méta table → pas d'exception, retourne les données MV seules."""
    code = "98010001"
    insert_station(code, "Station Hybrid 10", department=98)
    insert_mv_record(
        code, "Station Hybrid 10", "all_time", None, "TX", 38.0, dt.date(2003, 7, 15)
    )

    ds = HybridTemperatureRecordsDataSource()

    # Simuler une erreur DB (ex. table absente) sur _get_cutoff_date
    with patch.object(
        ds, "_get_cutoff_date", side_effect=Exception("table does not exist")
    ):
        result = ds.fetch_records(
            TemperatureRecordsRequest(period_type="all_time", type_records="hot")
        )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 38.0
