from __future__ import annotations

import datetime as dt
from unittest.mock import patch

import pytest

from weather.data_sources.timescale import HybridTemperatureRecordsDataSource
from weather.services.temperature_records.types import TemperatureRecordsRequest
from weather.tests.helpers.horaire import insert_mv_quotidienne_realtime
from weather.tests.helpers.records import (
    insert_mv_record,
    insert_mv_records_absolus_par_mois,
    set_cutoff,
)
from weather.tests.helpers.stations import insert_station

# Valeurs neutres pour remplir le côté opposé de tn/tx (v_quotidienne exige
# tntxm IS NOT NULL, donc tn ET tx doivent être présents).
_FILLER_TN = 5.0
_FILLER_TX = 5.0

# =========================
# Tests
# =========================


@pytest.mark.django_db
def test_no_cutoff_returns_mv_only():
    """Méta table vide → retourne uniquement les données MV, sans query à chaud."""
    code = "76116001"
    insert_station(code, "Station Hybrid 1", departement=76)
    insert_mv_record(
        code, "Station Hybrid 1", "all_time", None, "TX", 38.0, dt.date(2003, 7, 15)
    )
    # Ne pas appeler set_cutoff → méta vide

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 38.0


@pytest.mark.django_db
def test_cutoff_future_no_new_data():
    """Cutoff = aujourd'hui, données Quotidienne avant cutoff → aucun ajout."""
    code = "76116002"
    insert_station(code, "Station Hybrid 2", departement=76)
    insert_mv_record(
        code, "Station Hybrid 2", "all_time", None, "TX", 38.0, dt.date(2003, 7, 15)
    )
    set_cutoff(dt.date.today())

    # Donnée avant cutoff (2024)
    insert_mv_quotidienne_realtime(code, dt.date(2024, 7, 1), tn=_FILLER_TN, tx=35.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 38.0


@pytest.mark.django_db
def test_new_hot_record_after_cutoff_is_added():
    """Record chaud battu après cutoff → ligne ajoutée dans les résultats."""
    code = "76116003"
    insert_station(code, "Station Hybrid 3", departement=76)
    insert_mv_record(
        code, "Station Hybrid 3", "all_time", None, "TX", 38.0, dt.date(2003, 7, 15)
    )
    cutoff = dt.date(2025, 12, 31)
    set_cutoff(cutoff)

    insert_mv_quotidienne_realtime(code, dt.date(2026, 7, 15), tn=_FILLER_TN, tx=45.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    values = [e.record_value for e in entries]
    assert 38.0 in values
    assert 45.0 in values
    assert entries[-1].record_date == dt.date(2026, 7, 15)


@pytest.mark.django_db
def test_value_below_seed_not_added():
    """Valeur après cutoff inférieure au seed → pas ajoutée."""
    code = "76116004"
    insert_station(code, "Station Hybrid 4", departement=76)
    insert_mv_record(
        code, "Station Hybrid 4", "all_time", None, "TX", 42.0, dt.date(2019, 7, 25)
    )
    set_cutoff(dt.date(2025, 12, 31))

    insert_mv_quotidienne_realtime(code, dt.date(2026, 7, 1), tn=_FILLER_TN, tx=39.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 42.0


@pytest.mark.django_db
def test_new_station_after_cutoff_gets_first_record():
    """Nouvelle station absente de la MV → son premier jour après cutoff = record."""
    code = "76116005"
    insert_station(code, "Station Hybrid 5", departement=76)
    set_cutoff(dt.date(2025, 12, 31))

    insert_mv_quotidienne_realtime(code, dt.date(2026, 3, 15), tn=_FILLER_TN, tx=22.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 22.0
    assert entries[0].record_date == dt.date(2026, 3, 15)


@pytest.mark.django_db
def test_new_cold_record_after_cutoff():
    """Record froid battu après cutoff → type_records='cold'."""
    code = "76116006"
    insert_station(code, "Station Hybrid 6", departement=76)
    insert_mv_record(
        code, "Station Hybrid 6", "all_time", None, "TN", -20.0, dt.date(1985, 1, 16)
    )
    set_cutoff(dt.date(2025, 12, 31))

    insert_mv_quotidienne_realtime(code, dt.date(2026, 1, 10), tn=-25.0, tx=_FILLER_TX)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="cold")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    values = [e.record_value for e in entries]
    assert -20.0 in values
    assert -25.0 in values


@pytest.mark.django_db
def test_cold_above_seed_not_added():
    """TN après cutoff supérieure (moins froid) au seed → pas ajoutée."""
    code = "76116007"
    insert_station(code, "Station Hybrid 7", departement=76)
    insert_mv_record(
        code, "Station Hybrid 7", "all_time", None, "TN", -20.0, dt.date(1985, 1, 16)
    )
    set_cutoff(dt.date(2025, 12, 31))

    insert_mv_quotidienne_realtime(code, dt.date(2026, 1, 5), tn=-15.0, tx=_FILLER_TX)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="cold")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == -20.0


@pytest.mark.django_db
def test_month_filter_respected():
    """Filtre period_type='month' : données hors mois ignorées dans le hot calc."""
    code = "76116008"
    insert_station(code, "Station Hybrid 8", departement=76)
    insert_mv_record(
        code, "Station Hybrid 8", "month", "7", "TX", 38.0, dt.date(2003, 7, 15)
    )
    set_cutoff(dt.date(2025, 12, 31))

    # Donnée en août (hors mois 7)
    insert_mv_quotidienne_realtime(code, dt.date(2026, 8, 10), tn=_FILLER_TN, tx=50.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="month", type_records="hot", month=7)
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 38.0


@pytest.mark.django_db
def test_season_filter_respected():
    """Filtre period_type='season' : données hors saison ignorées dans le hot calc."""
    code = "76116009"
    insert_station(code, "Station Hybrid 9", departement=76)
    insert_mv_record(
        code, "Station Hybrid 9", "season", "summer", "TX", 40.0, dt.date(2003, 8, 12)
    )
    set_cutoff(dt.date(2025, 12, 31))

    # Donnée en janvier (hors été)
    insert_mv_quotidienne_realtime(code, dt.date(2026, 1, 5), tn=_FILLER_TN, tx=50.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(
            period_type="season", type_records="hot", season="summer"
        )
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 40.0


@pytest.mark.django_db
def test_all_months_mode_enriches_per_month_seeds():
    """period_type='month' sans month : l'enrichissement post-cutoff compare
    chaque ligne post-cutoff au seed du mois où elle tombe (per-month seeds)."""
    code = "76116011"
    insert_station(code, "Station Hybrid 11", departement=76)
    insert_mv_record(
        code, "Station Hybrid 11", "month", "7", "TX", 38.0, dt.date(2003, 7, 15)
    )
    insert_mv_record(
        code, "Station Hybrid 11", "month", "8", "TX", 35.0, dt.date(2001, 8, 10)
    )
    set_cutoff(dt.date(2025, 12, 31))

    # 2026-07-01 tx=50 : bat le seed de juillet (38) → nouveau record
    insert_mv_quotidienne_realtime(code, dt.date(2026, 7, 1), tn=_FILLER_TN, tx=50.0)
    # 2026-08-05 tx=30 : sous le seed d'août (35) → pas un nouveau record
    insert_mv_quotidienne_realtime(code, dt.date(2026, 8, 5), tn=_FILLER_TN, tx=30.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="month", type_records="hot", month=None)
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    values = [e.record_value for e in entries]
    # MV : 38 et 35. Post-cutoff : 50 (juillet, bat 38) ; 30 (août, sous 35) ignoré
    assert 38.0 in values
    assert 35.0 in values
    assert 50.0 in values
    assert 30.0 not in values


@pytest.mark.django_db
def test_all_seasons_mode_enriches_per_season_seeds():
    """period_type='season' sans season : enrichissement post-cutoff comparé au
    seed de la saison où tombe chaque ligne (per-season seeds)."""
    code = "76116012"
    insert_station(code, "Station Hybrid 12", departement=76)
    insert_mv_record(
        code, "Station Hybrid 12", "season", "summer", "TX", 40.0, dt.date(2003, 8, 12)
    )
    insert_mv_record(
        code, "Station Hybrid 12", "season", "winter", "TX", 12.0, dt.date(2010, 1, 5)
    )
    set_cutoff(dt.date(2025, 12, 31))

    # 2026-07-01 (summer) tx=55 : bat le seed été (40) → nouveau record
    insert_mv_quotidienne_realtime(code, dt.date(2026, 7, 1), tn=_FILLER_TN, tx=55.0)
    # 2026-02-10 (winter) tx=8 : sous le seed hiver (12) → pas un nouveau record
    insert_mv_quotidienne_realtime(code, dt.date(2026, 2, 10), tn=_FILLER_TN, tx=8.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="season", type_records="hot", season=None)
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    values = [e.record_value for e in entries]
    assert 40.0 in values
    assert 12.0 in values
    assert 55.0 in values
    assert 8.0 not in values


@pytest.mark.django_db
def test_all_months_date_filter_excludes_outside_range():
    """Export use case : month=None + date_start/date_end → seuls les records dans la fenêtre."""
    code = "76116013"
    insert_station(code, "Station Export Date", departement=76)

    # Record dans la fenêtre (2024-06)
    insert_mv_record(
        code, "Station Export Date", "month", "6", "TX", 38.0, dt.date(2024, 6, 15)
    )
    # Record hors fenêtre (2003-07)
    insert_mv_record(
        code, "Station Export Date", "month", "7", "TX", 42.0, dt.date(2003, 7, 15)
    )

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(
            period_type="month",
            type_records="hot",
            month=None,
            date_start=dt.date(2024, 1, 1),
            date_end=dt.date(2024, 12, 31),
        )
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    values = {e.record_value for e in entries}
    assert 38.0 in values
    assert 42.0 not in values


@pytest.mark.django_db
def test_after_cutoff_date_filter_excludes_outside_range():
    """date_start/date_end filtre aussi les records post-cutoff hors de la fenêtre."""
    code = "76116014"
    insert_station(code, "Station Post Cutoff Date", departement=76)
    insert_mv_record(
        code,
        "Station Post Cutoff Date",
        "all_time",
        None,
        "TX",
        38.0,
        dt.date(2003, 7, 15),
    )
    set_cutoff(dt.date(2025, 12, 31))

    # Record post-cutoff hors fenêtre (avant date_start) — ne bat pas le seed
    insert_mv_quotidienne_realtime(code, dt.date(2026, 1, 5), tn=_FILLER_TN, tx=35.0)
    # Record post-cutoff dans la fenêtre — bat le seed de 38.0
    insert_mv_quotidienne_realtime(code, dt.date(2026, 6, 10), tn=_FILLER_TN, tx=45.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(
            period_type="all_time",
            type_records="hot",
            date_start=dt.date(2026, 6, 1),
            date_end=dt.date(2026, 12, 31),
        )
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    values = {e.record_value for e in entries}
    assert 45.0 in values
    assert 35.0 not in values


@pytest.mark.django_db
def test_meta_table_absent_falls_back_to_mv():
    """Erreur DB sur la méta table → pas d'exception, retourne les données MV seules."""
    code = "76116010"
    insert_station(code, "Station Hybrid 10", departement=76)
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

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert len(entries) == 1
    assert entries[0].record_value == 38.0


@pytest.mark.django_db
def test_new_temperature_in_realtime_pipeline_appears_as_new_record():
    """
    Variante "avant/après" : un premier appel renvoie le record historique
    de la MV figée ; une nouvelle température arrive ensuite via le pipeline
    temps-réel (simulé par insert dans mv_quotidienne_realtime, état post-
    refresh) ; le deuxième appel doit la voir comme nouveau record.
    """
    code = "76116015"
    insert_station(code, "Station Two-Step", departement=76)
    insert_mv_record(
        code, "Station Two-Step", "all_time", None, "TX", 38.0, dt.date(2003, 7, 15)
    )
    set_cutoff(dt.date(2025, 12, 31))

    ds = HybridTemperatureRecordsDataSource()
    request = TemperatureRecordsRequest(period_type="all_time", type_records="hot")

    first = ds.fetch_records(request)
    first_for_station = [e for e in first.entries if e.station_id.strip() == code]
    assert [(e.record_date, e.record_value) for e in first_for_station] == [
        (dt.date(2003, 7, 15), 38.0)
    ]

    insert_mv_quotidienne_realtime(code, dt.date(2026, 7, 15), tn=_FILLER_TN, tx=45.0)

    second = ds.fetch_records(request)
    second_for_station = [e for e in second.entries if e.station_id.strip() == code]
    values = {(e.record_date, e.record_value) for e in second_for_station}
    assert (dt.date(2003, 7, 15), 38.0) in values
    assert (dt.date(2026, 7, 15), 45.0) in values


@pytest.mark.django_db
def test_record_on_cutoff_date_is_detected():
    """Un record qui tombe exactement le jour de la cutoff_date doit être
    détecté (borne de la query post-cutoff inclut la cutoff)."""
    code = "76116016"
    insert_station(code, "Station Cutoff Day Table", departement=76)
    insert_mv_record(
        code,
        "Station Cutoff Day Table",
        "all_time",
        None,
        "TX",
        38.0,
        dt.date(2003, 7, 15),
    )
    cutoff = dt.date(2026, 5, 23)
    set_cutoff(cutoff)
    insert_mv_quotidienne_realtime(code, cutoff, tn=_FILLER_TN, tx=45.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    values = {(e.record_date, e.record_value) for e in entries}
    assert (cutoff, 45.0) in values, (
        f"Le record du jour de cutoff ({cutoff}) manque dans la réponse : " f"{entries}"
    )


@pytest.mark.django_db
def test_record_present_in_mv_and_realtime_is_not_counted_twice():
    """Un record présent à la fois dans mv_records_battus ET dans
    mv_quotidienne_realtime (même valeur) ne doit pas apparaître deux fois."""
    code = "76116017"
    insert_station(code, "Station No Dup Table", departement=76)
    same_day = dt.date(2026, 7, 15)
    insert_mv_record(
        code, "Station No Dup Table", "all_time", None, "TX", 42.0, same_day
    )
    set_cutoff(dt.date(2025, 12, 31))
    insert_mv_quotidienne_realtime(code, same_day, tn=_FILLER_TN, tx=42.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    on_same_day = [e for e in entries if e.record_date == same_day]
    assert (
        len(on_same_day) == 1
    ), f"Le record du {same_day} apparaît {len(on_same_day)} fois : {on_same_day}"
    assert on_same_day[0].record_value == 42.0


@pytest.mark.django_db
def test_stale_mv_record_does_not_duplicate_with_fresher_realtime():
    """Si mv_records_battus a une valeur figée plus basse (38) que le pipeline
    temps-réel (45) le même jour, la réponse ne doit contenir qu'une seule
    ligne pour ce jour, avec la valeur la plus haute (la fraîche)."""
    code = "76116018"
    insert_station(code, "Station Stale MV Table", departement=76)
    same_day = dt.date(2026, 7, 15)
    insert_mv_record(
        code, "Station Stale MV Table", "all_time", None, "TX", 38.0, same_day
    )
    set_cutoff(dt.date(2025, 12, 31))
    insert_mv_quotidienne_realtime(code, same_day, tn=_FILLER_TN, tx=45.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    on_same_day = [e for e in entries if e.record_date == same_day]
    assert (
        len(on_same_day) == 1
    ), f"Le record du {same_day} apparaît {len(on_same_day)} fois : {on_same_day}"
    assert on_same_day[0].record_value == 45.0


@pytest.mark.django_db
def test_absolute_record_predates_50_year_filter_seeds_correctly():
    """Cas MARIGNANE pour l'endpoint table : record absolu cold de mai (0°C
    le 1960-05-01) absent de mv_records_battus (filtre 50-ans) mais présent
    dans v_records_absolus_par_type. Une TN du jour à 12.3°C ne doit PAS
    être détectée comme nouveau record."""
    code = "13054001"
    insert_station(
        code,
        "MARIGNANE",
        departement=13,
        first_temperature_date=dt.date(1920, 1, 1),
    )
    # mv_records_battus vide pour ce station/mois ; seed via les absolus
    insert_mv_records_absolus_par_mois(
        station_code=code,
        month=5,
        txx_max=35.0,
        txx_max_date=dt.date(2000, 5, 15),
        tnn_min=0.0,
        tnn_min_date=dt.date(1960, 5, 1),
    )
    set_cutoff(dt.date(2025, 12, 31))
    insert_mv_quotidienne_realtime(code, dt.date(2026, 5, 22), tn=12.3, tx=20.0)

    ds = HybridTemperatureRecordsDataSource()
    result = ds.fetch_records(
        TemperatureRecordsRequest(
            period_type="month",
            type_records="cold",
            month=5,
            date_start=dt.date(2026, 1, 1),
            date_end=dt.date(2026, 5, 22),
        )
    )

    entries = [e for e in result.entries if e.station_id.strip() == code]
    assert entries == [], (
        "12.3°C ne doit pas battre le record absolu May de 0°C, "
        f"mais le hybride retourne : {entries}"
    )
