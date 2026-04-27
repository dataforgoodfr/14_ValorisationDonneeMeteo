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
STATION_ID_1 = "01269001"
STATION_ID_2 = "01333001"


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
        STATION_ID_1,
        "Station 1",
        classe_recente=classe1,
        annee_de_creation=annee_creation1,
    )
    insert_station(
        STATION_ID_2,
        "Station 2",
        classe_recente=classe2,
        annee_de_creation=annee_creation2,
    )
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)
    # Patch annee_de_fermeture directly since insert_station doesn't expose it
    from django.db import connection

    for code, annee in (
        (STATION_ID_1, annee_fermeture1),
        (STATION_ID_2, annee_fermeture2),
    ):
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
    GIVEN  STATION_ID_1 classe 1, STATION_ID_2 classe 3
    WHEN   classe_recente_min=2
    THEN   Seule STATION_ID_2 (classe 3) est retournée
    """
    insert_station(STATION_ID_1, "Station 1", classe_recente=1)
    insert_station(STATION_ID_2, "Station 2", classe_recente=3)
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(classe_recente_min=2)
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {STATION_ID_2}


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_classe_recente_max():
    """
    GIVEN  STATION_ID_1 classe 1, STATION_ID_2 classe 3
    WHEN   classe_recente_max=2
    THEN   Seule STATION_ID_1 (classe 1) est retournée
    """
    insert_station(STATION_ID_1, "Station 1", classe_recente=1)
    insert_station(STATION_ID_2, "Station 2", classe_recente=3)
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(classe_recente_max=2)
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {STATION_ID_1}


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_classe_recente_range():
    """
    GIVEN  STATION_ID_1 classe 1, STATION_ID_2 classe 3
    WHEN   classe_recente_min=2, classe_recente_max=4
    THEN   Seule STATION_ID_2 (classe 3) est retournée
    """
    insert_station(STATION_ID_1, "Station 1", classe_recente=1)
    insert_station(STATION_ID_2, "Station 2", classe_recente=3)
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(classe_recente_min=2, classe_recente_max=4)
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {STATION_ID_2}


# ---------------------------------------------------------------------------
# date_de_creation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_date_de_creation_max():
    """
    GIVEN  STATION_ID_1 créée en 1920, STATION_ID_2 créée en 1980
    WHEN   date_de_creation_max=1950-01-01 (→ année 1950)
    THEN   Seule STATION_ID_1 (1920) est retournée
    """
    insert_station(
        STATION_ID_1, "Station Ancienne", classe_recente=1, annee_de_creation=1920
    )
    insert_station(
        STATION_ID_2, "Station Récente", classe_recente=1, annee_de_creation=1980
    )
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(date_de_creation_max=dt.date(1950, 1, 1))
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {STATION_ID_1}
    assert result.stations[0].date_de_creation == dt.date(1920, 1, 1)


@pytest.mark.django_db
def test_fetch_station_overview_filters_by_date_de_creation_min():
    """
    GIVEN  STATION_ID_1 créée en 1920, STATION_ID_2 créée en 1980
    WHEN   date_de_creation_min=1950-01-01 (→ année 1950)
    THEN   Seule STATION_ID_2 (1980) est retournée
    """
    insert_station(
        STATION_ID_1, "Station Ancienne", classe_recente=1, annee_de_creation=1920
    )
    insert_station(
        STATION_ID_2, "Station Récente", classe_recente=1, annee_de_creation=1980
    )
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(date_de_creation_min=dt.date(1950, 1, 1))
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {STATION_ID_2}
    assert result.stations[0].date_de_creation == dt.date(1980, 1, 1)


# ---------------------------------------------------------------------------
# date_de_fermeture
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_fetch_station_overview_fermeture_max_excludes_open_stations():
    """
    GIVEN  STATION_ID_1 fermée en 2000, STATION_ID_2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_max=2010-01-01
    THEN   Seule STATION_ID_1 (fermée en 2000 ≤ 2010) est retournée ;
           STATION_ID_2 (NULL) est exclue car on cherche les fermées avant la date
    """
    insert_station(
        STATION_ID_1, "Station Fermée", classe_recente=1, annee_de_creation=1950
    )
    insert_station(
        STATION_ID_2, "Station Ouverte", classe_recente=1, annee_de_creation=1950
    )
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)
    from django.db import connection

    with connection.cursor() as cur:
        cur.execute(
            'UPDATE public."station_creation_date" SET "annee_de_fermeture" = 2000 WHERE station_code = %s',
            [STATION_ID_1],
        )

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(date_de_fermeture_max=dt.date(2010, 1, 1))
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {STATION_ID_1}
    assert result.stations[0].date_de_fermeture == dt.date(2000, 12, 31)


@pytest.mark.django_db
def test_fetch_station_overview_fermeture_min_alone_includes_open_stations():
    """
    GIVEN  STATION_ID_1 fermée en 1990, STATION_ID_2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_min=2000-01-01 seul
    THEN   STATION_ID_2 (NULL = toujours ouverte) est incluse ;
           STATION_ID_1 (fermée en 1990 < 2000) est exclue
    """
    insert_station(
        STATION_ID_1,
        "Station Fermée Ancienne",
        classe_recente=1,
        annee_de_creation=1950,
    )
    insert_station(
        STATION_ID_2, "Station Ouverte", classe_recente=1, annee_de_creation=1950
    )
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)
    from django.db import connection

    with connection.cursor() as cur:
        cur.execute(
            'UPDATE public."station_creation_date" SET "annee_de_fermeture" = 1990 WHERE station_code = %s',
            [STATION_ID_1],
        )

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(date_de_fermeture_min=dt.date(2000, 1, 1))
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {STATION_ID_2}
    assert result.stations[0].date_de_fermeture is None


@pytest.mark.django_db
def test_fetch_station_overview_fermeture_min_and_max_excludes_open_stations():
    """
    GIVEN  STATION_ID_1 fermée en 2005, STATION_ID_2 toujours ouverte (annee_de_fermeture NULL)
    WHEN   date_de_fermeture_min=2000-01-01 ET date_de_fermeture_max=2010-01-01
    THEN   Seule STATION_ID_1 (fermée dans l'intervalle) est retournée ;
           STATION_ID_2 (NULL) est exclue car les deux bornes imposent une fermeture effective
    """
    insert_station(
        STATION_ID_1,
        "Station Fermée Intervalle",
        classe_recente=1,
        annee_de_creation=1950,
    )
    insert_station(
        STATION_ID_2, "Station Ouverte", classe_recente=1, annee_de_creation=1950
    )
    insert_station_daily_baseline(STATION_ID_1, DATE.month, DATE.day, 10.0)
    insert_station_daily_baseline(STATION_ID_2, DATE.month, DATE.day, 10.0)
    insert_quotidienne(DATE, STATION_ID_1, 12.0)
    insert_quotidienne(DATE, STATION_ID_2, 12.0)
    from django.db import connection

    with connection.cursor() as cur:
        cur.execute(
            'UPDATE public."station_creation_date" SET "annee_de_fermeture" = 2005 WHERE station_code = %s',
            [STATION_ID_1],
        )

    result = TimescaleTemperatureDeviationDailyDataSource().fetch_station_overview(
        make_query(
            date_de_fermeture_min=dt.date(2000, 1, 1),
            date_de_fermeture_max=dt.date(2010, 1, 1),
        )
    )

    assert result.pagination.total_count == 1
    assert _ids(result) == {STATION_ID_1}
