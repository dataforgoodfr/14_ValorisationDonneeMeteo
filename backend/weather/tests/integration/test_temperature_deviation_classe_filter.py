"""
Tests du filtre SQL sur classe_recente pour l'endpoint déviation.

Vérifie que le seuil de qualité (classe_recente BETWEEN 1 AND 4) appliqué
dans TimescaleTemperatureDeviationDailyDataSource est correctement respecté
sur les valeurs limites.

Chaque test suit le schéma :
  GIVEN  — une station avec une classe donnée
  WHEN   — on appelle fetch_station_overview sans filtre explicite sur la classe
  THEN   — la station apparaît ou non selon son éligibilité
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import TimescaleTemperatureDeviationDailyDataSource
from weather.services.temperature_deviation.types import (
    TemperatureDeviationOverviewQuery,
)
from weather.tests.helpers.itn import insert_quotidienne
from weather.tests.helpers.stations import insert_station
from weather.tests.helpers.stations_baseline import insert_station_daily_baseline

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OBSERVATION_DATE = dt.date(2024, 1, 1)


def make_overview_query(**kwargs) -> TemperatureDeviationOverviewQuery:
    defaults = {
        "date_start": OBSERVATION_DATE,
        "date_end": OBSERVATION_DATE,
        "offset": 0,
        "limit": 10,
    }
    return TemperatureDeviationOverviewQuery(**{**defaults, **kwargs})


def _station_ids_in_overview(result) -> set[str]:
    return {s.station_id for s in result.stations}


def _insert_station_with_deviation_data(code: str, classe: int) -> None:
    insert_station(code, f"Station classe {classe}", classe_recente=classe)
    insert_station_daily_baseline(
        code, OBSERVATION_DATE.month, OBSERVATION_DATE.day, 10.0
    )
    insert_quotidienne(OBSERVATION_DATE, code, 12.0)


# ---------------------------------------------------------------------------
# Filtre BETWEEN 1 AND 4
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_deviation_classe_3_is_included():
    """
    GIVEN  Une station de classe 3 (incluse dans les deux endpoints)
    WHEN   fetch_station_overview sans filtre explicite
    THEN   La station apparaît dans les résultats
    """
    code = "99811001"
    _insert_station_with_deviation_data(code, classe=3)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_overview_query()
    )

    assert code in _station_ids_in_overview(result)


@pytest.mark.django_db
def test_deviation_classe_4_is_included():
    """
    GIVEN  Une station de classe 4 (valeur limite haute autorisée)
    WHEN   fetch_station_overview sans filtre explicite
    THEN   La station apparaît dans les résultats
    """
    code = "99812001"
    _insert_station_with_deviation_data(code, classe=4)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_overview_query()
    )

    assert code in _station_ids_in_overview(result)


@pytest.mark.django_db
def test_deviation_classe_5_is_excluded():
    """
    GIVEN  Une station de classe 5 (première valeur hors seuil)
    WHEN   fetch_station_overview sans filtre explicite
    THEN   La station est absente des résultats
    """
    code = "99813001"
    _insert_station_with_deviation_data(code, classe=5)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_overview_query()
    )

    assert code not in _station_ids_in_overview(result)
