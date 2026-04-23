"""
Tests business de TimescaleRecordsDataSource.

Chaque test suit le schéma :
  GIVEN  — une station avec des mesures historiques connues
  WHEN   — on appelle fetch_records avec un scénario métier précis
  THEN   — on obtient exactement les dates et valeurs attendues
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import TimescaleRecordsDataSource
from weather.services.records.types import RecordsQuery
from weather.tests.conftest import insert_mv_record, set_cutoff
from weather.tests.helpers.stations import insert_station

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PAST_CUTOFF = dt.date(2024, 12, 31)


def make_query(**kwargs) -> RecordsQuery:
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


def _station_by_id(results, station_id: str):
    return next((s for s in results if s.id.strip() == station_id), None)


# ---------------------------------------------------------------------------
# Scénario 1 — Records all-time chauds : progression sur plusieurs années
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_alltime_hot_records_progression():
    """
    GIVEN  La station 99001001 a battu son record de chaleur 3 fois :
             - 1990-07-20 : 35.0 °C (premier record, pas de précédent)
             - 2003-08-05 : 42.5 °C  (dépasse 35.0)
             - 2019-06-28 : 45.1 °C  (dépasse 42.5)
             Et une mesure non-record : 2010-07-15 : 38.0 °C (< 42.5 au moment t)
    WHEN   fetch_records(record_scope=all_time, type_records=hot, record_kind=historical)
    THEN   On obtient exactement 3 records pour cette station :
             dates [1990-07-20, 2003-08-05, 2019-06-28], valeurs [35.0, 42.5, 45.1]
    """
    code = "99001001"
    insert_station(code, "Station Canicule", departement=13)
    set_cutoff(PAST_CUTOFF)

    insert_mv_record(
        code,
        "Station Canicule",
        "all_time",
        None,
        "TX",
        35.0,
        dt.date(1990, 7, 20),
        department=13,
    )
    insert_mv_record(
        code,
        "Station Canicule",
        "all_time",
        None,
        "TX",
        42.5,
        dt.date(2003, 8, 5),
        department=13,
    )
    insert_mv_record(
        code,
        "Station Canicule",
        "all_time",
        None,
        "TX",
        45.1,
        dt.date(2019, 6, 28),
        department=13,
    )
    # 38.0 °C (2010-07-15) n'est pas inséré dans la MV : la MV ne contient que les vrais records progressifs

    ds = TimescaleRecordsDataSource()
    results = ds.fetch_records(make_query())

    station = _station_by_id(results, code)
    assert station is not None, "La station doit apparaître dans les résultats"

    hot_dates = {r.date for r in station.hot_records}
    hot_values = {r.value for r in station.hot_records}

    assert dt.date(1990, 7, 20) in hot_dates
    assert dt.date(2003, 8, 5) in hot_dates
    assert dt.date(2019, 6, 28) in hot_dates
    assert dt.date(2010, 7, 15) not in hot_dates, "38.0 n'est pas un record (< 42.5)"
    assert hot_values == {35.0, 42.5, 45.1}


# ---------------------------------------------------------------------------
# Scénario 2 — Records mensuels : seules les mesures du bon mois comptent
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_monthly_hot_records_only_target_month():
    """
    GIVEN  La station 99002001 a battu son record mensuel en juillet :
             - 2000-07-15 : 38.0 °C (premier record juillet)
             - 2022-07-03 : 41.0 °C (bat le record juillet)
           Et une mesure en août (non juillet) :
             - 2022-08-10 : 50.0 °C (hors scope mensuel juillet)
    WHEN   fetch_records(record_scope=monthly, month=7, type_records=hot)
    THEN   On obtient 2 records pour juillet, la mesure d'août est absente
    """
    code = "99002001"
    insert_station(code, "Station Juillet", departement=69)
    set_cutoff(PAST_CUTOFF)

    insert_mv_record(
        code,
        "Station Juillet",
        "month",
        "7",
        "TX",
        38.0,
        dt.date(2000, 7, 15),
        department=69,
    )
    insert_mv_record(
        code,
        "Station Juillet",
        "month",
        "7",
        "TX",
        41.0,
        dt.date(2022, 7, 3),
        department=69,
    )
    # Mesure août — ne doit pas apparaître dans les records juillet
    insert_mv_record(
        code,
        "Station Juillet",
        "month",
        "8",
        "TX",
        50.0,
        dt.date(2022, 8, 10),
        department=69,
    )

    ds = TimescaleRecordsDataSource()
    results = ds.fetch_records(make_query(record_scope="monthly", month=7))

    station = _station_by_id(results, code)
    assert station is not None

    hot_dates = {r.date for r in station.hot_records}
    assert dt.date(2000, 7, 15) in hot_dates
    assert dt.date(2022, 7, 3) in hot_dates
    assert dt.date(2022, 8, 10) not in hot_dates, "Mesure août hors scope juillet"


# ---------------------------------------------------------------------------
# Scénario 3 — Records all-time froids : deux stations, valeurs correctes
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_alltime_cold_records_two_stations():
    """
    GIVEN  Station A (99003001) : record froid le 1985-01-16 à -22.0 °C
           Station B (99003002) : record froid le 1963-02-11 à -18.5 °C
    WHEN   fetch_records(record_scope=all_time, type_records=cold)
    THEN   Station A a cold_records contenant (-22.0, 1985-01-16)
           Station B a cold_records contenant (-18.5, 1963-02-11)
           Les hot_records sont vides (type_records=cold)
    """
    code_a, code_b = "99003001", "99003002"
    insert_station(code_a, "Station Grand Froid A", departement=67)
    insert_station(code_b, "Station Grand Froid B", departement=57)
    set_cutoff(PAST_CUTOFF)

    insert_mv_record(
        code_a,
        "Station Grand Froid A",
        "all_time",
        None,
        "TN",
        -22.0,
        dt.date(1985, 1, 16),
        department=67,
    )
    insert_mv_record(
        code_b,
        "Station Grand Froid B",
        "all_time",
        None,
        "TN",
        -18.5,
        dt.date(1963, 2, 11),
        department=57,
    )

    ds = TimescaleRecordsDataSource()
    results = ds.fetch_records(make_query(type_records="cold"))

    sta = _station_by_id(results, code_a)
    stb = _station_by_id(results, code_b)

    assert sta is not None
    assert stb is not None

    assert sta.hot_records == ()
    assert len(sta.cold_records) == 1
    assert sta.cold_records[0].value == -22.0
    assert sta.cold_records[0].date == dt.date(1985, 1, 16)

    assert stb.cold_records[0].value == -18.5
    assert stb.cold_records[0].date == dt.date(1963, 2, 11)


# ---------------------------------------------------------------------------
# Scénario 4 — record_kind=absolute : un seul record par station (le dernier)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_absolute_kind_returns_only_last_record_per_station():
    """
    GIVEN  La station 99004001 a battu son record chaud 3 fois :
             - 1990-07-20 : 33.0 °C
             - 2003-08-05 : 40.0 °C
             - 2019-06-28 : 44.0 °C  (record en vigueur)
    WHEN   fetch_records(record_kind=absolute, type_records=hot)
    THEN   Un seul record hot est retourné : (44.0, 2019-06-28)
    """
    code = "99004001"
    insert_station(code, "Station Absolu", departement=75)
    set_cutoff(PAST_CUTOFF)

    insert_mv_record(
        code,
        "Station Absolu",
        "all_time",
        None,
        "TX",
        33.0,
        dt.date(1990, 7, 20),
        department=75,
    )
    insert_mv_record(
        code,
        "Station Absolu",
        "all_time",
        None,
        "TX",
        40.0,
        dt.date(2003, 8, 5),
        department=75,
    )
    insert_mv_record(
        code,
        "Station Absolu",
        "all_time",
        None,
        "TX",
        44.0,
        dt.date(2019, 6, 28),
        department=75,
    )

    ds = TimescaleRecordsDataSource()
    results = ds.fetch_records(make_query(record_kind="absolute"))

    station = _station_by_id(results, code)
    assert station is not None
    assert (
        len(station.hot_records) == 1
    ), "record_kind=absolute → un seul record par station"
    assert station.hot_records[0].value == 44.0
    assert station.hot_records[0].date == dt.date(2019, 6, 28)


# ---------------------------------------------------------------------------
# Scénario 5 — Filtre par département
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_department_filter_excludes_other_departments():
    """
    GIVEN  Station 99005001 (dept 13, Marseille) et Station 99005002 (dept 69, Lyon)
           Les deux ont un record all-time chaud
    WHEN   fetch_records avec departments=["13"]
    THEN   Seule la station 99005001 (dept 13) apparaît dans les résultats
    """
    code_13, code_69 = "99005001", "99005002"
    insert_station(code_13, "Station Marseille", departement=13)
    insert_station(code_69, "Station Lyon", departement=69)
    set_cutoff(PAST_CUTOFF)

    insert_mv_record(
        code_13,
        "Station Marseille",
        "all_time",
        None,
        "TX",
        40.0,
        dt.date(2019, 7, 28),
        department=13,
    )
    insert_mv_record(
        code_69,
        "Station Lyon",
        "all_time",
        None,
        "TX",
        37.5,
        dt.date(2019, 7, 25),
        department=69,
    )

    ds = TimescaleRecordsDataSource()
    results = ds.fetch_records(make_query(departments=("13",)))

    ids = {s.id.strip() for s in results}
    assert code_13 in ids
    assert (
        code_69 not in ids
    ), "Station Lyon (dept 69) ne doit pas apparaître dans dept=13"
