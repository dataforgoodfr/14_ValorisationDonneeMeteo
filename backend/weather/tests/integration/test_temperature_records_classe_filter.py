"""
Tests du filtre SQL sur classe_recente pour l'endpoint records.

Vérifie que le seuil de qualité (classe_recente BETWEEN 1 AND 3) appliqué
dans TimescaleRecordsDataSource est correctement respecté sur les valeurs limites.

Chaque test suit le schéma :
  GIVEN  — une station avec une classe donnée
  WHEN   — on appelle fetch_records sans filtre explicite sur la classe
  THEN   — la station apparaît ou non selon son éligibilité
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import (
    TimescaleRecordsDataSource,
    TimescaleTemperatureDeviationDailyDataSource,
)
from weather.services.records.types import RecordsQuery
from weather.services.temperature_deviation.types import (
    TemperatureDeviationOverviewQuery,
)
from weather.tests.conftest import insert_mv_record, set_cutoff
from weather.tests.helpers.itn import insert_quotidienne
from weather.tests.helpers.stations import insert_station
from weather.tests.helpers.stations_baseline import insert_station_daily_baseline

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PAST_CUTOFF = dt.date(2024, 12, 31)
OBSERVATION_DATE = dt.date(2024, 1, 1)


def make_records_query(**kwargs) -> RecordsQuery:
    defaults = {
        "date_start": None,
        "date_end": None,
        "station_ids": (),
        "departments": (),
        "record_kind": "historical",
        "record_scope": "all_time",
        "type_records": "hot",
        "temperature_min": None,
        "temperature_max": None,
    }
    return RecordsQuery(**{**defaults, **kwargs})


def make_overview_query(**kwargs) -> TemperatureDeviationOverviewQuery:
    defaults = {
        "date_start": OBSERVATION_DATE,
        "date_end": OBSERVATION_DATE,
        "offset": 0,
        "limit": 10,
    }
    return TemperatureDeviationOverviewQuery(**{**defaults, **kwargs})


def _station_ids_in_records(results) -> set[str]:
    return {s.id.strip() for s in results.entries}


def _station_ids_in_overview(result) -> set[str]:
    return {s.station_id for s in result.stations}


def _insert_station_with_record(code: str, classe: int) -> None:
    insert_station(code, f"Station classe {classe}", classe_recente=classe)
    set_cutoff(PAST_CUTOFF)
    insert_mv_record(
        code,
        f"Station classe {classe}",
        "all_time",
        None,
        "TX",
        40.0,
        dt.date(2003, 8, 5),
    )


# ---------------------------------------------------------------------------
# Filtre BETWEEN 1 AND 3
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_records_classe_1_is_included():
    """
    GIVEN  Une station de classe 1 (classe minimale)
    WHEN   fetch_records sans filtre explicite
    THEN   La station apparaît dans les résultats
    """
    code = "99801001"
    _insert_station_with_record(code, classe=1)

    results = TimescaleRecordsDataSource().fetch_records(make_records_query())

    assert code in _station_ids_in_records(results)


@pytest.mark.django_db
def test_records_classe_3_is_included():
    """
    GIVEN  Une station de classe 3 (valeur limite haute autorisée)
    WHEN   fetch_records sans filtre explicite
    THEN   La station apparaît dans les résultats
    """
    code = "99802001"
    _insert_station_with_record(code, classe=3)

    results = TimescaleRecordsDataSource().fetch_records(make_records_query())

    assert code in _station_ids_in_records(results)


@pytest.mark.django_db
def test_records_classe_4_is_excluded():
    """
    GIVEN  Une station de classe 4 (première valeur hors seuil)
    WHEN   fetch_records sans filtre explicite
    THEN   La station est absente des résultats
    """
    code = "99803001"
    _insert_station_with_record(code, classe=4)

    results = TimescaleRecordsDataSource().fetch_records(make_records_query())

    assert code not in _station_ids_in_records(results)


@pytest.mark.django_db
def test_records_classe_5_is_excluded():
    """
    GIVEN  Une station de classe 5 (classe maximale, hors seuil)
    WHEN   fetch_records sans filtre explicite
    THEN   La station est absente des résultats
    """
    code = "99804001"
    _insert_station_with_record(code, classe=5)

    results = TimescaleRecordsDataSource().fetch_records(make_records_query())

    assert code not in _station_ids_in_records(results)


# ---------------------------------------------------------------------------
# Asymétrie avec la déviation — classe 4
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_classe_4_excluded_from_records_but_included_in_deviation():
    """
    GIVEN  Une station de classe 4 avec un record ET des données de déviation
    WHEN   On appelle les deux datasources
    THEN   La station est absente des records (seuil 1-3)
           et présente dans la déviation (seuil 1-4)
    """
    code = "99820001"
    insert_station(code, "Station classe 4 mixte", classe_recente=4)
    set_cutoff(PAST_CUTOFF)
    insert_mv_record(
        code,
        "Station classe 4 mixte",
        "all_time",
        None,
        "TX",
        40.0,
        dt.date(2003, 8, 5),
    )
    insert_station_daily_baseline(
        code, OBSERVATION_DATE.month, OBSERVATION_DATE.day, 10.0
    )
    insert_quotidienne(OBSERVATION_DATE, code, 12.0)

    records_results = TimescaleRecordsDataSource().fetch_records(make_records_query())
    deviation_result = (
        TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
            make_overview_query()
        )
    )

    assert code not in _station_ids_in_records(
        records_results
    ), "classe 4 exclue des records"
    assert code in _station_ids_in_overview(
        deviation_result
    ), "classe 4 incluse dans la déviation"
