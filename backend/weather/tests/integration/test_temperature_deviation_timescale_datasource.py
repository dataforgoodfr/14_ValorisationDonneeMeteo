from __future__ import annotations

import datetime as dt

import pytest
from django.db import connection

from weather.data_sources.timescale import (
    TimescaleTemperatureDeviationDailyDataSource,
)
from weather.services.temperature_deviation.types import DailyDeviationSeriesQuery

# =========================
# Helpers SQL
# =========================


def insert_station(code: str, name: str = "Station test") -> None:
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
                 1, 'horaire',
                 '1', 1,
                 0.0, 0.0, 0.0, '1')
            """,
            {
                "created": now,
                "updated": now,
                "id": code,
                "name": name,
            },
        )


def insert_quotidienne(day: dt.date, code: str, tntxm: float) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Quotidienne"
                ("NUM_POSTE","NOM_USUEL","LAT","LON","ALTI","AAAAMMJJ","TNTXM")
            VALUES
                (%(code)s, %(name)s, 0, 0, 0, %(day)s, %(tntxm)s)
            ON CONFLICT ("NUM_POSTE","AAAAMMJJ")
            DO UPDATE SET "TNTXM" = EXCLUDED."TNTXM"
            """,
            {
                "code": code,
                "name": f"ST {code}",
                "day": day,
                "tntxm": tntxm,
            },
        )


def refresh_baseline_mv() -> None:
    with connection.cursor() as cur:
        cur.execute(
            "REFRESH MATERIALIZED VIEW public.baseline_station_daily_mean_1991_2020"
        )


# =========================
# Tests
# =========================


@pytest.mark.django_db
def test_fetch_stations_daily_series_happy_path():
    station_code = "01269001"

    insert_station(station_code, "Station 01269001")

    # --- baseline (>= 24 années requises)
    for year in range(1991, 2015):
        insert_quotidienne(dt.date(year, 1, 1), station_code, 10.0)
        insert_quotidienne(dt.date(year, 1, 2), station_code, 12.0)

    refresh_baseline_mv()

    # --- observations
    insert_quotidienne(dt.date(2024, 1, 1), station_code, 14.0)
    insert_quotidienne(dt.date(2024, 1, 2), station_code, 13.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        station_ids=(station_code,),
        include_national=False,
    )

    result = ds.fetch_stations_daily_series(query)

    assert len(result) == 1

    s = result[0]

    assert s.station_id == station_code
    assert s.station_name == "Station 01269001"

    assert [p.date for p in s.points] == [
        dt.date(2024, 1, 1),
        dt.date(2024, 1, 2),
    ]

    # valeurs observées
    assert s.points[0].temperature == 14.0
    assert s.points[1].temperature == 13.0

    # baseline issue de la MV
    assert s.points[0].baseline_mean == pytest.approx(10.0)
    assert s.points[1].baseline_mean == pytest.approx(12.0)


@pytest.mark.django_db
def test_fetch_stations_daily_series_filters_out_missing_baseline():
    station_code = "01269001"

    insert_station(station_code, "Station 01269001")

    # pas assez d'historique → baseline absente
    insert_quotidienne(dt.date(2024, 1, 3), station_code, 15.0)

    refresh_baseline_mv()

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 3),
        date_end=dt.date(2024, 1, 3),
        station_ids=(station_code,),
        include_national=False,
    )

    result = ds.fetch_stations_daily_series(query)

    # doit être filtré
    assert result == []


@pytest.mark.django_db
def test_fetch_stations_daily_series_multiple_stations():
    s1 = "01269001"
    s2 = "01333001"

    insert_station(s1, "Station 1")
    insert_station(s2, "Station 2")

    # baseline pour les deux
    for year in range(1991, 2015):
        insert_quotidienne(dt.date(year, 1, 1), s1, 10.0)
        insert_quotidienne(dt.date(year, 1, 1), s2, 5.0)

    refresh_baseline_mv()

    # observations
    insert_quotidienne(dt.date(2024, 1, 1), s1, 12.0)
    insert_quotidienne(dt.date(2024, 1, 1), s2, 6.0)

    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        station_ids=(s1, s2),
        include_national=False,
    )

    result = ds.fetch_stations_daily_series(query)

    assert len(result) == 2

    # ordre conservé
    assert [s.station_id for s in result] == [s1, s2]


@pytest.mark.django_db
def test_fetch_national_daily_series_not_implemented():
    ds = TimescaleTemperatureDeviationDailyDataSource()

    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 3),
        station_ids=("01269001",),
        include_national=True,
    )

    with pytest.raises(NotImplementedError):
        ds.fetch_national_daily_series(query)
