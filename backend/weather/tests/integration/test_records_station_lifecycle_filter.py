"""
Tests des filtres sur classe_recente, date_de_creation et date_de_fermeture
pour MaterializedTemperatureRecordsDataSource (endpoint /temperature/records/).

Chaque test suit le schéma :
  GIVEN  — deux stations aux caractéristiques contrastées
  WHEN   — fetch_records avec un filtre sur le critère en question
  THEN   — seule la station éligible apparaît dans les résultats
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.db import connection

from weather.data_sources.timescale import MaterializedTemperatureRecordsDataSource
from weather.services.temperature_records.types import TemperatureRecordsRequest
from weather.tests.conftest import insert_mv_record, set_cutoff
from weather.tests.helpers.stations import insert_station

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PAST_CUTOFF = dt.date(2024, 12, 31)
STATION_ID_1 = "98200001"
STATION_ID_2 = "98200002"

BASE_REQUEST = TemperatureRecordsRequest(period_type="all_time", type_records="hot")


def make_request(**kwargs) -> TemperatureRecordsRequest:
    return TemperatureRecordsRequest(
        period_type="all_time", type_records="hot", **kwargs
    )


def _insert_station_with_mv(
    code: str,
    name: str,
    *,
    classe: int,
    annee_de_creation: int = 1950,
) -> None:
    insert_station(
        code,
        name,
        classe_recente=classe,
        annee_de_creation=annee_de_creation,
    )
    set_cutoff(PAST_CUTOFF)
    insert_mv_record(code, name, "all_time", None, "TX", 40.0, dt.date(2003, 8, 5))


def _set_annee_fermeture(code: str, annee: int | None) -> None:
    with connection.cursor() as cur:
        cur.execute(
            'UPDATE public."station_creation_date" SET "annee_de_fermeture" = %s'
            " WHERE station_code = %s",
            [annee, code],
        )


def _station_ids(results) -> set[str]:
    return {e.station_id.strip() for e in results}


# ---------------------------------------------------------------------------
# classe_recente
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_records_filters_by_classe_recente_min():
    """
    GIVEN  STATION_ID_1 classe 1, STATION_ID_2 classe 3
    WHEN   classe_recente_min=2
    THEN   Seule STATION_ID_2 (classe 3) est retournée
    """
    _insert_station_with_mv(STATION_ID_1, "Station Classe 1", classe=1)
    _insert_station_with_mv(STATION_ID_2, "Station Classe 3", classe=3)

    ds = MaterializedTemperatureRecordsDataSource()
    results = ds.fetch_records(make_request(classe_recente_min=2))

    assert STATION_ID_2 in _station_ids(results)
    assert STATION_ID_1 not in _station_ids(results)


@pytest.mark.django_db
def test_fetch_records_filters_by_classe_recente_max():
    """
    GIVEN  STATION_ID_1 classe 1, STATION_ID_2 classe 3
    WHEN   classe_recente_max=2
    THEN   Seule STATION_ID_1 (classe 1) est retournée
    """
    _insert_station_with_mv(STATION_ID_1, "Station Classe 1", classe=1)
    _insert_station_with_mv(STATION_ID_2, "Station Classe 3", classe=3)

    ds = MaterializedTemperatureRecordsDataSource()
    results = ds.fetch_records(make_request(classe_recente_max=2))

    assert STATION_ID_1 in _station_ids(results)
    assert STATION_ID_2 not in _station_ids(results)


@pytest.mark.django_db
def test_fetch_records_filters_by_classe_recente_range():
    """
    GIVEN  STATION_ID_1 classe 1, STATION_ID_2 classe 3
    WHEN   classe_recente_min=2, classe_recente_max=3
    THEN   Seule STATION_ID_2 est retournée
    """
    _insert_station_with_mv(STATION_ID_1, "Station Classe 1", classe=1)
    _insert_station_with_mv(STATION_ID_2, "Station Classe 3", classe=3)

    ds = MaterializedTemperatureRecordsDataSource()
    results = ds.fetch_records(make_request(classe_recente_min=2, classe_recente_max=3))

    assert STATION_ID_2 in _station_ids(results)
    assert STATION_ID_1 not in _station_ids(results)


# ---------------------------------------------------------------------------
# date_de_creation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_records_filters_by_date_de_creation_max():
    """
    GIVEN  STATION_ID_1 créée en 1920, STATION_ID_2 créée en 1980
    WHEN   date_de_creation_max=1950-01-01
    THEN   Seule STATION_ID_1 (1920) est retournée
    """
    _insert_station_with_mv(
        STATION_ID_1, "Station Ancienne", classe=1, annee_de_creation=1920
    )
    _insert_station_with_mv(
        STATION_ID_2, "Station Récente", classe=1, annee_de_creation=1980
    )

    ds = MaterializedTemperatureRecordsDataSource()
    results = ds.fetch_records(make_request(date_de_creation_max=dt.date(1950, 1, 1)))

    assert STATION_ID_1 in _station_ids(results)
    assert STATION_ID_2 not in _station_ids(results)

    creation_dates = {
        e.date_de_creation for e in results if e.station_id.strip() == STATION_ID_1
    }
    assert creation_dates == {dt.date(1920, 1, 1)}


@pytest.mark.django_db
def test_fetch_records_filters_by_date_de_creation_min():
    """
    GIVEN  STATION_ID_1 créée en 1920, STATION_ID_2 créée en 1980
    WHEN   date_de_creation_min=1950-01-01
    THEN   Seule STATION_ID_2 (1980) est retournée
    """
    _insert_station_with_mv(
        STATION_ID_1, "Station Ancienne", classe=1, annee_de_creation=1920
    )
    _insert_station_with_mv(
        STATION_ID_2, "Station Récente", classe=1, annee_de_creation=1980
    )

    ds = MaterializedTemperatureRecordsDataSource()
    results = ds.fetch_records(make_request(date_de_creation_min=dt.date(1950, 1, 1)))

    assert STATION_ID_2 in _station_ids(results)
    assert STATION_ID_1 not in _station_ids(results)

    creation_dates = {
        e.date_de_creation for e in results if e.station_id.strip() == STATION_ID_2
    }
    assert creation_dates == {dt.date(1980, 1, 1)}


# ---------------------------------------------------------------------------
# date_de_fermeture
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_records_fermeture_max_excludes_open_stations():
    """
    GIVEN  STATION_ID_1 fermée en 2000, STATION_ID_2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_max=2010-01-01
    THEN   Seule STATION_ID_1 (fermée en 2000 ≤ 2010) est retournée ; STATION_ID_2 (NULL) est exclue
    """
    _insert_station_with_mv(STATION_ID_1, "Station Fermée", classe=1)
    _insert_station_with_mv(STATION_ID_2, "Station Ouverte", classe=1)
    _set_annee_fermeture(STATION_ID_1, 2000)

    ds = MaterializedTemperatureRecordsDataSource()
    results = ds.fetch_records(make_request(date_de_fermeture_max=dt.date(2010, 1, 1)))

    assert STATION_ID_1 in _station_ids(results)
    assert STATION_ID_2 not in _station_ids(results)

    fermeture_dates = {
        e.date_de_fermeture for e in results if e.station_id.strip() == STATION_ID_1
    }
    assert fermeture_dates == {dt.date(2000, 12, 31)}


@pytest.mark.django_db
def test_fetch_records_fermeture_min_alone_includes_open_stations():
    """
    GIVEN  STATION_ID_1 fermée en 1990, STATION_ID_2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_min=2000-01-01 seul
    THEN   STATION_ID_2 (NULL = ouverte) est incluse ; STATION_ID_1 (fermée en 1990 < 2000) est exclue
    """
    _insert_station_with_mv(STATION_ID_1, "Station Fermée Ancienne", classe=1)
    _insert_station_with_mv(STATION_ID_2, "Station Ouverte", classe=1)
    _set_annee_fermeture(STATION_ID_1, 1990)

    ds = MaterializedTemperatureRecordsDataSource()
    results = ds.fetch_records(make_request(date_de_fermeture_min=dt.date(2000, 1, 1)))

    assert STATION_ID_2 in _station_ids(results)
    assert STATION_ID_1 not in _station_ids(results)

    fermeture_dates = {
        e.date_de_fermeture for e in results if e.station_id.strip() == STATION_ID_2
    }
    assert fermeture_dates == {None}


@pytest.mark.django_db
def test_fetch_records_fermeture_min_and_max_excludes_open_stations():
    """
    GIVEN  STATION_ID_1 fermée en 2005, STATION_ID_2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_min=2000-01-01 ET date_de_fermeture_max=2010-01-01
    THEN   Seule STATION_ID_1 (fermée dans l'intervalle) est retournée ; STATION_ID_2 (NULL) est exclue
    """
    _insert_station_with_mv(STATION_ID_1, "Station Fermée Intervalle", classe=1)
    _insert_station_with_mv(STATION_ID_2, "Station Ouverte", classe=1)
    _set_annee_fermeture(STATION_ID_1, 2005)

    ds = MaterializedTemperatureRecordsDataSource()
    results = ds.fetch_records(
        make_request(
            date_de_fermeture_min=dt.date(2000, 1, 1),
            date_de_fermeture_max=dt.date(2010, 1, 1),
        )
    )

    assert STATION_ID_1 in _station_ids(results)
    assert STATION_ID_2 not in _station_ids(results)
