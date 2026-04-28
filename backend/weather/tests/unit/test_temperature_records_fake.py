import datetime as dt

from weather.data_sources.temperature_records_fake import (
    FakeTemperatureRecordsDataSource,
)
from weather.services.temperature_records.types import TemperatureRecordsRequest


def test_fake_records_hot_returns_non_empty_list():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    assert len(result.entries) >= 5
    assert all(e.record_value >= 30 for e in result.entries)


def test_fake_records_cold_returns_non_empty_list():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="cold")
    result = ds.fetch_records(req)

    assert len(result.entries) >= 5
    assert all(e.record_value <= 0 for e in result.entries)


def test_fake_records_month_period_type_does_not_raise():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="month", type_records="hot", month=7)
    result = ds.fetch_records(req)

    assert len(result.entries) >= 1


def test_fake_records_season_period_type_does_not_raise():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="season", type_records="cold", season="winter"
    )
    result = ds.fetch_records(req)

    assert len(result.entries) >= 1


def test_fake_records_all_time_period_type_does_not_raise():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    assert len(result.entries) >= 1


def test_fake_records_entries_have_correct_shape():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    for entry in result.entries:
        assert isinstance(entry.station_id, str)
        assert isinstance(entry.station_name, str)
        assert isinstance(entry.department, str)
        assert isinstance(entry.record_value, float)
        assert isinstance(entry.record_date, dt.date)


def test_fake_records_is_deterministic():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")

    r1 = ds.fetch_records(req)
    r2 = ds.fetch_records(req)

    assert r1 == r2


# ---------------------------------------------------------------------------
# Filtres classe_recente
# ---------------------------------------------------------------------------

# Les stations fake ont toutes classe_recente=1 et date_de_fermeture=None.


def test_fake_records_classe_recente_min_filters_out_lower():
    """classe_recente_min=2 → toutes les stations (classe 1) sont exclues."""
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time", type_records="hot", classe_recente_min=2
    )
    result = ds.fetch_records(req)

    assert result.entries == []


def test_fake_records_classe_recente_min_includes_matching():
    """classe_recente_min=1 → toutes les stations (classe 1) sont incluses."""
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time", type_records="hot", classe_recente_min=1
    )
    result = ds.fetch_records(req)

    assert len(result.entries) >= 5


def test_fake_records_classe_recente_max_includes_matching():
    """classe_recente_max=1 → toutes les stations (classe 1) sont incluses."""
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time", type_records="hot", classe_recente_max=1
    )
    result = ds.fetch_records(req)

    assert len(result.entries) >= 5


def test_fake_records_classe_recente_range_no_match():
    """classe_recente_min=2, classe_recente_max=5 → toutes exclues (toutes classe 1)."""
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        classe_recente_min=2,
        classe_recente_max=5,
    )
    result = ds.fetch_records(req)

    assert result.entries == []


# ---------------------------------------------------------------------------
# Filtres date_de_creation
# ---------------------------------------------------------------------------


def test_fake_records_date_de_creation_max_filters_recent_stations():
    """
    date_de_creation_max=1900-01-01 → seule LYON-BRON (1888) est incluse.
    ORLY (1921), BOURGES (1945), TOULOUSE (1947) sont exclues.
    """
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        date_de_creation_max=dt.date(1900, 1, 1),
    )
    result = ds.fetch_records(req)

    station_ids = {e.station_id for e in result.entries}
    assert station_ids == {"07481"}  # LYON-BRON uniquement


def test_fake_records_date_de_creation_min_filters_old_stations():
    """
    date_de_creation_min=1940-01-01 → BOURGES (1945) et TOULOUSE (1947) incluses.
    ORLY (1921) et LYON-BRON (1888) exclues.
    """
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        date_de_creation_min=dt.date(1940, 1, 1),
    )
    result = ds.fetch_records(req)

    station_ids = {e.station_id for e in result.entries}
    assert station_ids == {"07255", "07630"}  # BOURGES + TOULOUSE-BLAGNAC


# ---------------------------------------------------------------------------
# Filtres date_de_fermeture
# ---------------------------------------------------------------------------


def test_fake_records_fermeture_max_excludes_open_stations():
    """
    Toutes les stations fake ont date_de_fermeture=None.
    date_de_fermeture_max → stations NULL exclues → liste vide.
    """
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        date_de_fermeture_max=dt.date(2050, 1, 1),
    )
    result = ds.fetch_records(req)

    assert result.entries == []


def test_fake_records_fermeture_min_alone_includes_open_stations():
    """
    date_de_fermeture_min seul → stations NULL incluses.
    Toutes les stations fake ont date_de_fermeture=None → toutes incluses.
    """
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        date_de_fermeture_min=dt.date(2000, 1, 1),
    )
    result = ds.fetch_records(req)

    assert len(result.entries) >= 5


def test_fake_records_fermeture_min_and_max_excludes_open_stations():
    """
    date_de_fermeture_min + date_de_fermeture_max → stations NULL exclues → liste vide.
    """
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        date_de_fermeture_min=dt.date(1990, 1, 1),
        date_de_fermeture_max=dt.date(2020, 1, 1),
    )
    result = ds.fetch_records(req)

    assert result.entries == []
