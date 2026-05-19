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
def test_after_cutoff_record_before_50ans_is_excluded():
    """Record post-cutoff dont la date est < création+50 → exclu."""
    code = "76116001"
    # Créée en 2020, seuil = 2070-01-01
    insert_station(
        code,
        "Station Jeune",
        departement=76,
        first_temperature_date=dt.date(2020, 1, 1),
    )
    set_cutoff(dt.date(2025, 12, 31))

    # 2026 < 2030 → doit être ignoré
    insert_quotidienne(dt.date(2026, 7, 15), code, tx=45.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert entries == [], "Une station de moins de 50 ans ne doit pas apparaître"


@pytest.mark.django_db
def test_after_cutoff_record_exactly_at_50ans_is_included():
    """Record post-cutoff dont la date est exactement création+50 → inclus."""
    code = "76116002"
    # Créée il y a 50 ans, seuil = YYYY-01-01
    current_year = dt.date.today().year
    fifty_years_ago = current_year - 50
    insert_station(
        code,
        "Station 50ans pile",
        departement=76,
        first_temperature_date=dt.date(fifty_years_ago, 1, 1),
    )
    set_cutoff(dt.date(current_year - 1, 12, 31))

    # YYYY-01-01 == seuil → doit être inclus
    insert_quotidienne(dt.date(current_year, 1, 1), code, tx=30.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_date == dt.date(2026, 1, 1)


@pytest.mark.django_db
def test_after_cutoff_record_after_50ans_is_included():
    """Record post-cutoff dont la date est > création+50 → inclus normalement."""
    code = "76116003"
    # Créée en 1970, seuil = 2020-01-01
    insert_station(
        code,
        "Station Ancienne",
        departement=76,
        first_temperature_date=dt.date(1970, 1, 1),
    )
    set_cutoff(dt.date(2025, 12, 31))

    insert_quotidienne(dt.date(2026, 8, 10), code, tx=42.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 42.0


@pytest.mark.django_db
def test_after_cutoff_only_recent_records_cross_50ans_threshold():
    """Station avec records pré et post-seuil : seul le post-seuil apparaît."""
    code = "76116004"
    # Créée en 1962, seuil = 2012-01-01
    insert_station(
        code,
        "Station Mixte",
        departement=76,
        first_temperature_date=dt.date(1962, 1, 1),
    )
    set_cutoff(dt.date(2009, 12, 31))

    # 2010 < 2012 → exclu
    insert_quotidienne(dt.date(2010, 6, 1), code, tx=38.0)
    # 2014 >= 2012 → inclus
    insert_quotidienne(dt.date(2014, 7, 20), code, tx=41.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_date == dt.date(2014, 7, 20)
