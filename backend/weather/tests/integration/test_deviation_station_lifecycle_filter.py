"""
Tests des filtres sur classe_recente, date_de_creation et date_de_fermeture
pour fetch_station_overview (endpoint /temperature/deviation/).

Chaque test suit le schéma :
  GIVEN  — deux stations aux caractéristiques contrastées
  WHEN   — fetch_station_overview avec un filtre sur le critère en question
  THEN   — seule la station éligible apparaît dans les résultats
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

DATE = dt.date(2024, 1, 1)
S1 = "01269001"
S2 = "01333001"


def make_query(**kwargs) -> TemperatureDeviationOverviewQuery:
    defaults = {"date_start": DATE, "date_end": DATE, "offset": 0, "limit": 10}
    return TemperatureDeviationOverviewQuery(**{**defaults, **kwargs})


def _setup_two_stations(
    classe1: int,
    classe2: int,
    annee_creation1: int,
    annee_creation2: int,
    annee_fermeture1: int | None,
    annee_fermeture2: int | None,
) -> None:
    insert_station(
        S1, "Station 1", classe_recente=classe1, annee_de_creation=annee_creation1
    )
    insert_station(
        S2, "Station 2", classe_recente=classe2, annee_de_creation=annee_creation2
    )
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)
    # Patch annee_de_fermeture directly since insert_station doesn't expose it
    from django.db import connection

    for code, annee in ((S1, annee_fermeture1), (S2, annee_fermeture2)):
        with connection.cursor() as cur:
            cur.execute(
                'UPDATE public."station_creation_date" SET "annee_de_fermeture" = %s WHERE station_code = %s',
                [annee, code],
            )


def _ids(result) -> set[str]:
    return {s.station_id for s in result.stations}


# ---------------------------------------------------------------------------
# classe_recente
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_classe_recente_min():
    """
    GIVEN  S1 classe 1, S2 classe 3
    WHEN   classe_recente_min=2
    THEN   Seule S2 (classe 3) est retournée
    """
    insert_station(S1, "Station 1", classe_recente=1)
    insert_station(S2, "Station 2", classe_recente=3)
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(classe_recente_min=2)
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {S2}


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_classe_recente_max():
    """
    GIVEN  S1 classe 1, S2 classe 3
    WHEN   classe_recente_max=2
    THEN   Seule S1 (classe 1) est retournée
    """
    insert_station(S1, "Station 1", classe_recente=1)
    insert_station(S2, "Station 2", classe_recente=3)
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(classe_recente_max=2)
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {S1}


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_classe_recente_range():
    """
    GIVEN  S1 classe 1, S2 classe 3
    WHEN   classe_recente_min=2, classe_recente_max=4
    THEN   Seule S2 (classe 3) est retournée
    """
    insert_station(S1, "Station 1", classe_recente=1)
    insert_station(S2, "Station 2", classe_recente=3)
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(classe_recente_min=2, classe_recente_max=4)
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {S2}


# ---------------------------------------------------------------------------
# date_de_creation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_date_de_creation_max():
    """
    GIVEN  S1 créée en 1920, S2 créée en 1980
    WHEN   date_de_creation_max=1950-01-01 (→ année 1950)
    THEN   Seule S1 (1920) est retournée
    """
    insert_station(S1, "Station Ancienne", classe_recente=1, annee_de_creation=1920)
    insert_station(S2, "Station Récente", classe_recente=1, annee_de_creation=1980)
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(date_de_creation_max=dt.date(1950, 1, 1))
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {S1}
    assert result.stations[0].date_de_creation == dt.date(1920, 1, 1)


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_date_de_creation_min():
    """
    GIVEN  S1 créée en 1920, S2 créée en 1980
    WHEN   date_de_creation_min=1950-01-01 (→ année 1950)
    THEN   Seule S2 (1980) est retournée
    """
    insert_station(S1, "Station Ancienne", classe_recente=1, annee_de_creation=1920)
    insert_station(S2, "Station Récente", classe_recente=1, annee_de_creation=1980)
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(date_de_creation_min=dt.date(1950, 1, 1))
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {S2}
    assert result.stations[0].date_de_creation == dt.date(1980, 1, 1)


# ---------------------------------------------------------------------------
# date_de_fermeture
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_station_overview_fermeture_max_excludes_open_stations():
    """
    GIVEN  S1 fermée en 2000, S2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_max=2010-01-01
    THEN   Seule S1 (fermée en 2000 ≤ 2010) est retournée ;
           S2 (NULL) est exclue car on cherche les fermées avant la date
    """
    insert_station(S1, "Station Fermée", classe_recente=1, annee_de_creation=1950)
    insert_station(S2, "Station Ouverte", classe_recente=1, annee_de_creation=1950)
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)
    from django.db import connection

    with connection.cursor() as cur:
        cur.execute(
            'UPDATE public."station_creation_date" SET "annee_de_fermeture" = 2000 WHERE station_code = %s',
            [S1],
        )

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(date_de_fermeture_max=dt.date(2010, 1, 1))
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {S1}
    assert result.stations[0].date_de_fermeture == dt.date(2000, 12, 31)


@pytest.mark.django_db
def test_fetch_station_overview_fermeture_min_alone_includes_open_stations():
    """
    GIVEN  S1 fermée en 1990, S2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_min=2000-01-01 seul
    THEN   S2 (NULL = toujours ouverte) est incluse ;
           S1 (fermée en 1990 < 2000) est exclue
    """
    insert_station(
        S1, "Station Fermée Ancienne", classe_recente=1, annee_de_creation=1950
    )
    insert_station(S2, "Station Ouverte", classe_recente=1, annee_de_creation=1950)
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)
    from django.db import connection

    with connection.cursor() as cur:
        cur.execute(
            'UPDATE public."station_creation_date" SET "annee_de_fermeture" = 1990 WHERE station_code = %s',
            [S1],
        )

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(date_de_fermeture_min=dt.date(2000, 1, 1))
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {S2}
    assert result.stations[0].date_de_fermeture is None


@pytest.mark.django_db
def test_fetch_station_overview_fermeture_min_and_max_excludes_open_stations():
    """
    GIVEN  S1 fermée en 2005, S2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_min=2000-01-01 ET date_de_fermeture_max=2010-01-01
    THEN   Seule S1 (fermée dans l'intervalle) est retournée ;
           S2 (NULL) est exclue car les deux bornes imposent une fermeture effective
    """
    insert_station(
        S1, "Station Fermée Intervalle", classe_recente=1, annee_de_creation=1950
    )
    insert_station(S2, "Station Ouverte", classe_recente=1, annee_de_creation=1950)
    insert_station_daily_baseline(S1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(S2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, S1, 12.0)
    insert_quotidienne(DATE, S2, 12.0)
    from django.db import connection

    with connection.cursor() as cur:
        cur.execute(
            'UPDATE public."station_creation_date" SET "annee_de_fermeture" = 2005 WHERE station_code = %s',
            [S1],
        )

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(
            date_de_fermeture_min=dt.date(2000, 1, 1),
            date_de_fermeture_max=dt.date(2010, 1, 1),
        )
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {S1}
