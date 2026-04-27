"""
Tests pour le filtre 20 ans : un record n'est valide que si
record_date >= make_date(annee_de_creation + 20, 1, 1).
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import HybridTemperatureRecordsDataSource
from weather.services.temperature_records.types import TemperatureRecordsRequest
from weather.tests.conftest import (
    insert_quotidienne,
    set_cutoff,
)
from weather.tests.helpers.stations import insert_station


@pytest.mark.django_db
def test_after_cutoff_record_before_20ans_is_excluded():
    """Record post-cutoff dont la date est < création+20 → exclu."""
    code = "97001001"
    # Créée en 2010, seuil = 2030-01-01
    insert_station(code, "Station Jeune", departement=97, annee_de_creation=2010)
    set_cutoff(dt.date(2025, 12, 31))

    # 2026 < 2030 → doit être ignoré
    insert_quotidienne(dt.date(2026, 7, 15), code, tx=45.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert entries == [], "Une station de moins de 20 ans ne doit pas apparaître"


@pytest.mark.django_db
def test_after_cutoff_record_exactly_at_20ans_is_included():
    """Record post-cutoff dont la date est exactement création+20 → inclus."""
    code = "97002001"
    # Créée en 2006, seuil = 2026-01-01
    insert_station(code, "Station 20ans pile", departement=97, annee_de_creation=2006)
    set_cutoff(dt.date(2025, 12, 31))

    # 2026-01-01 == seuil → doit être inclus
    insert_quotidienne(dt.date(2026, 1, 1), code, tx=30.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_date == dt.date(2026, 1, 1)


@pytest.mark.django_db
def test_after_cutoff_record_after_20ans_is_included():
    """Record post-cutoff dont la date est > création+20 → inclus normalement."""
    code = "97003001"
    # Créée en 2000, seuil = 2020-01-01
    insert_station(code, "Station Ancienne", departement=97, annee_de_creation=2000)
    set_cutoff(dt.date(2025, 12, 31))

    insert_quotidienne(dt.date(2026, 8, 10), code, tx=42.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 42.0


@pytest.mark.django_db
def test_after_cutoff_only_recent_records_cross_20ans_threshold():
    """Station avec records pré et post-seuil : seul le post-seuil apparaît."""
    code = "97004001"
    # Créée en 2008, seuil = 2028-01-01
    insert_station(code, "Station Mixte", departement=97, annee_de_creation=2008)
    set_cutoff(dt.date(2025, 12, 31))

    # 2026 < 2028 → filtré
    insert_quotidienne(dt.date(2026, 6, 1), code, tx=38.0)
    # 2029 >= 2028 → inclus
    insert_quotidienne(dt.date(2029, 7, 20), code, tx=41.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_date == dt.date(2029, 7, 20)
