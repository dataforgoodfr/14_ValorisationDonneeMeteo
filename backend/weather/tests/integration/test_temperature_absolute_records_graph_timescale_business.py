from __future__ import annotations

import datetime as dt

import pytest
from django.db import connection

from weather.data_sources.timescale import TimescaleAbsoluteRecordsGraphDataSource
from weather.services.records_graph.types import RecordsGraphRequest
from weather.tests.helpers.stations import insert_station


def _req(**kwargs) -> RecordsGraphRequest:
    defaults = {
        "date_start": dt.date(1940, 1, 1),
        "date_end": dt.date(2025, 12, 31),
        "granularity": "year",
        "period_type": "all_time",
        "type_records": "hot",
        "month": None,
        "season": None,
        "territoire": "france",
        "territoire_id": None,
    }
    defaults.update(kwargs)
    return RecordsGraphRequest(**defaults)


def insert_mv_records_absolus_par_mois(
    *,
    station_code: str,
    month: int,
    txx_max: float,
    txx_max_date: str,
    tnn_min: float,
    tnn_min_date: str,
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_records_absolus_par_mois
                (station_code,     month,     txx_max,     txx_max_date,     tnn_min,     tnn_min_date)
            VALUES
                (%(station_code)s, %(month)s, %(txx_max)s, %(txx_max_date)s, %(tnn_min)s, %(tnn_min_date)s)
            """,
            {
                "station_code": station_code,
                "month": month,
                "txx_max": txx_max,
                "txx_max_date": txx_max_date,
                "tnn_min": tnn_min,
                "tnn_min_date": tnn_min_date,
            },
        )


@pytest.mark.django_db
def test_fetch_graph_returns_one_bucket_per_year():
    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2021, 12, 31),
        )
    )

    buckets = [b.bucket for b in result.buckets]
    assert buckets == ["2019", "2020", "2021"]


@pytest.mark.django_db
def test_fetch_graph_counts_hot_records():
    insert_station("76116001")
    insert_station("76116002")
    insert_mv_records_absolus_par_mois(
        station_code="76116001",
        month=7,
        txx_max=41.0,
        txx_max_date="2019-07-21",
        tnn_min=-41.0,
        tnn_min_date="1919-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116002",
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-22",
        tnn_min=-42.0,
        tnn_min_date="1919-07-02",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="hot",
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_absolus == 2


@pytest.mark.django_db
def test_fetch_graph_cold_records_not_counted_as_hot():
    insert_station("76116003")
    insert_mv_records_absolus_par_mois(
        station_code="76116003",
        month=2,
        txx_max=20.0,
        txx_max_date="1912-02-23",
        tnn_min=-20.0,
        tnn_min_date="2012-02-03",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2012, 1, 1),
            date_end=dt.date(2012, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="hot",
        )
    )

    bucket_2012 = next(b for b in result.buckets if b.bucket == "2012")
    assert bucket_2012.nb_records_absolus == 0


@pytest.mark.django_db
def test_fetch_graph_month_granularity_buckets():
    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 3, 31),
            granularity="month",
        )
    )

    buckets = [b.bucket for b in result.buckets]
    assert buckets == ["2019-01", "2019-02", "2019-03"]


@pytest.mark.django_db
def test_fetch_graph_day_granularity_buckets():
    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 7, 1),
            date_end=dt.date(2019, 7, 3),
            granularity="day",
        )
    )

    buckets = [b.bucket for b in result.buckets]
    assert buckets == ["2019-07-01", "2019-07-02", "2019-07-03"]


@pytest.mark.django_db
def test_fetch_graph_empty_buckets_return_zero():
    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(1900, 1, 1),
            date_end=dt.date(1900, 12, 31),
            granularity="year",
        )
    )

    assert len(result.buckets) == 1
    assert result.buckets[0].bucket == "1900"
    assert result.buckets[0].nb_records_absolus == 0


@pytest.mark.django_db
def test_fetch_graph_filter_by_department():
    insert_station("94003001", departement=94)
    insert_station("75116001", departement=75)
    insert_mv_records_absolus_par_mois(
        station_code="94003001",
        month=7,
        txx_max=39.0,
        txx_max_date="2019-07-21",
        tnn_min=-39.0,
        tnn_min_date="1919-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code="75116001",
        month=7,
        txx_max=38.0,
        txx_max_date="2019-07-21",
        tnn_min=-38.0,
        tnn_min_date="1919-07-01",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="hot",
            territoire="department",
            territoire_id="94",
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_absolus == 1


@pytest.mark.django_db
def test_fetch_graph_filter_by_station():
    """
    GIVEN  Deux stations, chacune avec un record en juillet 2019
    WHEN   territoire="station", territoire_id=<une station>
    THEN   Seul le record de la station filtrée est retourné
    """
    insert_station("76116050")
    insert_station("76116051")
    insert_mv_records_absolus_par_mois(
        station_code="76116050",
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-20",
        tnn_min=-42.0,
        tnn_min_date="1919-07-10",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116051",
        month=7,
        txx_max=38.0,
        txx_max_date="2019-07-21",
        tnn_min=-38.0,
        tnn_min_date="1919-07-01",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="hot",
            territoire="station",
            territoire_id="76116050",
        )
    )

    assert {(r.station_id, r.valeur, r.date) for r in result.records} == {
        ("76116050", 42.0, dt.date(2019, 7, 20)),
    }


@pytest.mark.django_db
def test_fetch_graph_excludes_stations_younger_than_50_years():
    """
    GIVEN  Une station ancienne (50+ ans) et une station jeune (< 50 ans)
    WHEN   fetch_graph
    THEN   Seule la station ancienne apparaît ; la jeune est filtrée par
           v_station_records (WHERE first_temperature_date <= now() - 50 years)
    """
    # NOTE: La date "2020-01-01" ci-dessous doit être mise à jour avant 2050,
    # sinon la station "jeune" deviendra elle-même 50+ ans et le test échouera.
    insert_station("76116060")
    insert_station("76116061", first_temperature_date=dt.date(2020, 1, 1))
    insert_mv_records_absolus_par_mois(
        station_code="76116060",
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-20",
        tnn_min=-42.0,
        tnn_min_date="1919-07-10",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116061",
        month=7,
        txx_max=43.0,
        txx_max_date="2026-07-21",
        tnn_min=-43.0,
        tnn_min_date="2021-07-01",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="hot",
        )
    )

    assert {(r.station_id, r.valeur, r.date) for r in result.records} == {
        ("76116060", 42.0, dt.date(2019, 7, 20)),
    }


@pytest.mark.django_db
def test_fetch_graph_all_aggregates_hot_and_cold():
    insert_station("76116004")
    insert_station("76116005")
    insert_mv_records_absolus_par_mois(
        station_code="76116004",
        month=7,
        txx_max=42.0,
        txx_max_date="2020-07-24",
        tnn_min=-42.0,
        tnn_min_date="1920-07-04",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116005",
        month=1,
        txx_max=15.0,
        txx_max_date="1920-01-25",
        tnn_min=-15.0,
        tnn_min_date="2020-01-05",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2020, 1, 1),
            date_end=dt.date(2020, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="all",
        )
    )

    bucket_2020 = next(b for b in result.buckets if b.bucket == "2020")
    assert bucket_2020.nb_records_absolus == 2  # 1 hot + 1 cold


@pytest.mark.django_db
def test_fetch_graph_records_match_inserted_data():
    insert_station("76116006", "TestStation", departement=76)
    insert_mv_records_absolus_par_mois(
        station_code="76116006",
        month=8,
        txx_max=39.5,
        txx_max_date="2021-08-26",
        tnn_min=-39.5,
        tnn_min_date="1921-08-06",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2021, 1, 1),
            date_end=dt.date(2021, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="hot",
        )
    )

    assert len(result.records) >= 1
    match = next((r for r in result.records if r.station_id == "76116006"), None)
    assert match is not None
    assert match.station_name == "TestStation"
    assert match.type_records == "hot"
    assert match.valeur == 39.5
    assert match.date == dt.date(2021, 8, 26)


@pytest.mark.django_db
def test_fetch_graph_period_type_month():
    insert_station("76116007")
    insert_mv_records_absolus_par_mois(
        station_code="76116007",
        month=7,
        txx_max=43.0,
        txx_max_date="2019-07-27",
        tnn_min=-43.0,
        tnn_min_date="1919-07-07",
    )
    # Record d'un autre mois : ne doit pas être compté avec month=7
    insert_mv_records_absolus_par_mois(
        station_code="76116007",
        month=8,
        txx_max=43.0,
        txx_max_date="2019-08-27",
        tnn_min=-43.0,
        tnn_min_date="1919-08-07",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="month",
            month=7,
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_absolus == 1


@pytest.mark.django_db
def test_fetch_graph_period_type_month_all_months():
    insert_station("76116008")
    insert_station("76116009")
    insert_mv_records_absolus_par_mois(
        station_code="76116008",
        month=7,
        txx_max=43.0,
        txx_max_date="2019-07-28",
        tnn_min=-43.0,
        tnn_min_date="1919-07-08",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116009",
        month=8,
        txx_max=41.0,
        txx_max_date="2019-08-29",
        tnn_min=-41.0,
        tnn_min_date="1919-08-09",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="month",
            month=None,
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_absolus == 2  # juillet + août, pas all_time


@pytest.mark.django_db
def test_fetch_graph_period_type_season_all_seasons():
    insert_station("76116011")
    insert_station("76116012")
    insert_mv_records_absolus_par_mois(
        station_code="76116011",
        month=7,
        txx_max=43.0,
        txx_max_date="2019-07-21",
        tnn_min=-43.0,
        tnn_min_date="1919-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116012",
        month=4,
        txx_max=30.0,
        txx_max_date="2019-04-22",
        tnn_min=-30.0,
        tnn_min_date="1919-04-02",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="season",
            season=None,
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_absolus == 2  # summer + spring, pas all_time


@pytest.mark.django_db
def test_fetch_graph_period_type_season_specific_winter():
    """
    GIVEN  Un record en décembre (winter), un en janvier (winter), un en juillet (summer)
    WHEN   period_type=season, season="winter"
    THEN   Les deux records d'hiver sont comptés ; celui d'été est exclu
    """
    insert_station("76116020")
    insert_station("76116021")
    insert_station("76116022")
    insert_mv_records_absolus_par_mois(
        station_code="76116020",
        month=12,
        txx_max=18.0,
        txx_max_date="2019-12-15",
        tnn_min=-18.0,
        tnn_min_date="1919-12-15",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116021",
        month=1,
        txx_max=15.0,
        txx_max_date="2019-01-15",
        tnn_min=-15.0,
        tnn_min_date="1919-01-15",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116022",
        month=7,
        txx_max=40.0,
        txx_max_date="2019-07-15",
        tnn_min=-40.0,
        tnn_min_date="1919-07-15",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="season",
            season="winter",
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_absolus == 2  # décembre + janvier, pas juillet


@pytest.mark.django_db
def test_fetch_graph_period_type_month_specific_excludes_other_months():
    insert_station("76116014")
    insert_station("76116015")
    insert_mv_records_absolus_par_mois(
        station_code="76116014",
        month=7,
        txx_max=43.0,
        txx_max_date="2019-07-24",
        tnn_min=-43.0,
        tnn_min_date="1919-07-14",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116015",
        month=8,
        txx_max=41.0,
        txx_max_date="2019-08-25",
        tnn_min=-41.0,
        tnn_min_date="1919-08-05",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="month",
            month=7,
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_absolus == 1  # juillet uniquement


@pytest.mark.django_db
def test_fetch_graph_season_keeps_only_best_record_per_station():
    """
    GIVEN  Une station avec 3 records dans les 3 mois d'hiver (déc, jan, fév),
           valeurs hot croissantes 10°C → 12°C → 15°C
    WHEN   period_type=season, season="winter", type_records="hot"
    THEN   Une seule ligne pour la station, avec la valeur max d'hiver (15°C en février)
    """
    insert_station("76116030")
    insert_mv_records_absolus_par_mois(
        station_code="76116030",
        month=12,
        txx_max=10.0,
        txx_max_date="2019-12-20",
        tnn_min=-10.0,
        tnn_min_date="1919-12-10",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116030",
        month=1,
        txx_max=12.0,
        txx_max_date="2019-01-20",
        tnn_min=-12.0,
        tnn_min_date="1919-01-10",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116030",
        month=2,
        txx_max=15.0,
        txx_max_date="2019-02-20",
        tnn_min=-15.0,
        tnn_min_date="1919-02-10",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="season",
            season="winter",
            type_records="hot",
        )
    )

    station_records = [r for r in result.records if r.station_id == "76116030"]
    assert {(r.valeur, r.date) for r in station_records} == {
        (15.0, dt.date(2019, 2, 20)),
    }


@pytest.mark.django_db
def test_fetch_graph_all_time_keeps_only_best_record_per_station():
    """
    GIVEN  Une station avec 3 records dans 3 mois différents (mars, juillet, novembre),
           valeurs hot : 20°C, 42°C, 25°C
    WHEN   period_type=all_time, type_records="hot"
    THEN   Une seule ligne pour la station, avec la valeur max all-time (42°C en juillet)
    """
    insert_station("76116031")
    insert_mv_records_absolus_par_mois(
        station_code="76116031",
        month=3,
        txx_max=20.0,
        txx_max_date="2019-03-21",
        tnn_min=-20.0,
        tnn_min_date="1919-03-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116031",
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-21",
        tnn_min=-42.0,
        tnn_min_date="1919-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116031",
        month=11,
        txx_max=25.0,
        txx_max_date="2019-11-21",
        tnn_min=-25.0,
        tnn_min_date="1919-11-01",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="hot",
        )
    )

    station_records = [r for r in result.records if r.station_id == "76116031"]
    assert {(r.valeur, r.date) for r in station_records} == {
        (42.0, dt.date(2019, 7, 21)),
    }


@pytest.mark.django_db
def test_fetch_graph_season_keeps_only_coldest_record_per_station():
    """
    GIVEN  Une station avec 3 records dans les 3 mois d'hiver (déc, jan, fév),
           valeurs cold décroissantes -10°C → -12°C → -15°C
    WHEN   period_type=season, season="winter", type_records="cold"
    THEN   Une seule ligne pour la station, avec la valeur min d'hiver (-15°C en février)
    """
    insert_station("76116032")
    insert_mv_records_absolus_par_mois(
        station_code="76116032",
        month=12,
        txx_max=10.0,
        txx_max_date="1919-12-22",
        tnn_min=-10.0,
        tnn_min_date="2019-12-02",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116032",
        month=1,
        txx_max=12.0,
        txx_max_date="1919-01-22",
        tnn_min=-12.0,
        tnn_min_date="2019-01-02",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116032",
        month=2,
        txx_max=15.0,
        txx_max_date="1919-02-22",
        tnn_min=-15.0,
        tnn_min_date="2019-02-02",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="season",
            season="winter",
            type_records="cold",
        )
    )

    station_records = [r for r in result.records if r.station_id == "76116032"]
    assert {(r.valeur, r.date) for r in station_records} == {
        (-15.0, dt.date(2019, 2, 2)),
    }


@pytest.mark.django_db
def test_fetch_graph_all_time_keeps_only_coldest_record_per_station():
    """
    GIVEN  Une station avec 3 records dans 3 mois différents (mars, juillet, novembre),
           valeurs cold : -20°C, -42°C, -25°C
    WHEN   period_type=all_time, type_records="cold"
    THEN   Une seule ligne pour la station, avec la valeur min all-time (-42°C en juillet)
    """
    insert_station("76116033")
    insert_mv_records_absolus_par_mois(
        station_code="76116033",
        month=3,
        txx_max=20.0,
        txx_max_date="1919-03-23",
        tnn_min=-20.0,
        tnn_min_date="2019-03-03",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116033",
        month=7,
        txx_max=42.0,
        txx_max_date="1919-07-23",
        tnn_min=-42.0,
        tnn_min_date="2019-07-03",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116033",
        month=11,
        txx_max=25.0,
        txx_max_date="1919-11-23",
        tnn_min=-25.0,
        tnn_min_date="2019-11-03",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="all_time",
            type_records="cold",
        )
    )

    station_records = [r for r in result.records if r.station_id == "76116033"]
    assert {(r.valeur, r.date) for r in station_records} == {
        (-42.0, dt.date(2019, 7, 3)),
    }


@pytest.mark.django_db
def test_fetch_graph_all_months_returns_one_row_per_month():
    """
    GIVEN  Une station avec 3 records dans 3 mois différents (avril, juillet, novembre)
    WHEN   period_type=month, month=None (tous les mois)
    THEN   3 lignes pour la station (une par mois), pas 1 ligne agrégée
    """
    insert_station("76116040")
    insert_mv_records_absolus_par_mois(
        station_code="76116040",
        month=4,
        txx_max=25.0,
        txx_max_date="2019-04-20",
        tnn_min=-25.0,
        tnn_min_date="1919-04-10",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116040",
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-20",
        tnn_min=-42.0,
        tnn_min_date="1919-07-10",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116040",
        month=11,
        txx_max=20.0,
        txx_max_date="2019-11-20",
        tnn_min=-20.0,
        tnn_min_date="1919-11-10",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="month",
            month=None,
            type_records="hot",
        )
    )

    station_records = [r for r in result.records if r.station_id == "76116040"]
    assert {(r.valeur, r.date) for r in station_records} == {
        (25.0, dt.date(2019, 4, 20)),
        (42.0, dt.date(2019, 7, 20)),
        (20.0, dt.date(2019, 11, 20)),
    }


@pytest.mark.django_db
def test_fetch_graph_all_seasons_returns_one_row_per_season():
    """
    GIVEN  Une station avec 3 records dans 3 saisons différentes
           (avril=printemps, juillet=été, novembre=automne)
    WHEN   period_type=season, season=None (toutes les saisons)
    THEN   3 lignes pour la station (une par saison), pas 1 ligne agrégée
    """
    insert_station("76116041")
    insert_mv_records_absolus_par_mois(
        station_code="76116041",
        month=4,
        txx_max=25.0,
        txx_max_date="2019-04-21",
        tnn_min=-25.0,
        tnn_min_date="1919-04-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116041",
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-21",
        tnn_min=-42.0,
        tnn_min_date="1919-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code="76116041",
        month=11,
        txx_max=20.0,
        txx_max_date="2019-11-21",
        tnn_min=-20.0,
        tnn_min_date="1919-11-01",
    )

    ds = TimescaleAbsoluteRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            period_type="season",
            season=None,
            type_records="hot",
        )
    )

    station_records = [r for r in result.records if r.station_id == "76116041"]
    assert {(r.valeur, r.date) for r in station_records} == {
        (25.0, dt.date(2019, 4, 21)),
        (42.0, dt.date(2019, 7, 21)),
        (20.0, dt.date(2019, 11, 21)),
    }
