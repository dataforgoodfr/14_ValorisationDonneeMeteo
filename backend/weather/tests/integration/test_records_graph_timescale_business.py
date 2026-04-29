from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import TimescaleRecordsGraphDataSource
from weather.services.records_graph.types import RecordsGraphRequest
from weather.tests.conftest import insert_mv_record


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


@pytest.mark.django_db
def test_fetch_graph_returns_one_bucket_per_year():
    ds = TimescaleRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(date_start=dt.date(2019, 1, 1), date_end=dt.date(2021, 12, 31))
    )

    buckets = [b.bucket for b in result.buckets]
    assert buckets == ["2019", "2020", "2021"]


@pytest.mark.django_db
def test_fetch_graph_counts_hot_records():
    insert_mv_record(
        station_code="76116001",
        station_name="Station Graph Test",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=42.0,
        date=dt.date(2019, 7, 25),
        department=76,
    )
    insert_mv_record(
        station_code="76116002",
        station_name="Station Graph Test 2",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=41.0,
        date=dt.date(2019, 7, 26),
        department=76,
    )

    ds = TimescaleRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_battus == 2


@pytest.mark.django_db
def test_fetch_graph_cold_records_not_counted_as_hot():
    insert_mv_record(
        station_code="76116003",
        station_name="Station Cold Graph",
        period_type="all_time",
        period_value=None,
        record_type="TN",
        value=-20.0,
        date=dt.date(2012, 2, 5),
        department=76,
    )

    ds = TimescaleRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2012, 1, 1),
            date_end=dt.date(2012, 12, 31),
            granularity="year",
            type_records="hot",
        )
    )

    bucket_2012 = next(b for b in result.buckets if b.bucket == "2012")
    assert bucket_2012.nb_records_battus == 0


@pytest.mark.django_db
def test_fetch_graph_month_granularity_buckets():
    ds = TimescaleRecordsGraphDataSource()
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
def test_fetch_graph_empty_buckets_return_zero():
    ds = TimescaleRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(1900, 1, 1),
            date_end=dt.date(1900, 12, 31),
            granularity="year",
        )
    )

    assert len(result.buckets) == 1
    assert result.buckets[0].bucket == "1900"
    assert result.buckets[0].nb_records_battus == 0


@pytest.mark.django_db
def test_fetch_graph_filter_by_department():
    insert_mv_record(
        station_code="94003001",
        station_name="Station Dept 94",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=39.0,
        date=dt.date(2019, 7, 25),
        department=94,
    )
    insert_mv_record(
        station_code="75116001",
        station_name="Station Dept 75",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=38.0,
        date=dt.date(2019, 7, 25),
        department=75,
    )

    ds = TimescaleRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2019, 1, 1),
            date_end=dt.date(2019, 12, 31),
            granularity="year",
            territoire="department",
            territoire_id="94",
        )
    )

    bucket_2019 = next(b for b in result.buckets if b.bucket == "2019")
    assert bucket_2019.nb_records_battus == 1


@pytest.mark.django_db
def test_fetch_graph_all_aggregates_hot_and_cold():
    insert_mv_record(
        station_code="76116004",
        station_name="S1",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=42.0,
        date=dt.date(2020, 7, 1),
        department=76,
    )
    insert_mv_record(
        station_code="76116005",
        station_name="S2",
        period_type="all_time",
        period_value=None,
        record_type="TN",
        value=-15.0,
        date=dt.date(2020, 1, 5),
        department=76,
    )

    ds = TimescaleRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2020, 1, 1),
            date_end=dt.date(2020, 12, 31),
            granularity="year",
            type_records="all",
        )
    )

    bucket_2020 = next(b for b in result.buckets if b.bucket == "2020")
    assert bucket_2020.nb_records_battus == 2  # 1 hot + 1 cold


@pytest.mark.django_db
def test_fetch_graph_records_match_inserted_data():
    insert_mv_record(
        station_code="76116006",
        station_name="TestStation",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=39.5,
        date=dt.date(2021, 8, 15),
        department=76,
    )

    ds = TimescaleRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2021, 1, 1),
            date_end=dt.date(2021, 12, 31),
            granularity="year",
            type_records="hot",
        )
    )

    assert len(result.records) >= 1
    match = next((r for r in result.records if r.station_id == "76116006"), None)
    assert match is not None
    assert match.station_name == "TestStation"
    assert match.type_records == "hot"
    assert match.valeur == 39.5
    assert match.date == dt.date(2021, 8, 15)


@pytest.mark.django_db
def test_fetch_graph_period_type_month():
    insert_mv_record(
        station_code="76116007",
        station_name="Station Period Month",
        period_type="month",
        period_value="7",
        record_type="TX",
        value=43.0,
        date=dt.date(2019, 7, 25),
        department=76,
    )
    # Record all_time : ne doit pas être compté avec period_type=month
    insert_mv_record(
        station_code="76116007",
        station_name="Station Period Month",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=43.0,
        date=dt.date(2019, 7, 25),
        department=76,
    )

    ds = TimescaleRecordsGraphDataSource()
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
    assert bucket_2019.nb_records_battus == 1


@pytest.mark.django_db
def test_fetch_graph_period_type_month_all_months():
    insert_mv_record(
        station_code="76116008",
        station_name="Station Juillet",
        period_type="month",
        period_value="7",
        record_type="TX",
        value=43.0,
        date=dt.date(2019, 7, 25),
        department=76,
    )
    insert_mv_record(
        station_code="76116009",
        station_name="Station Août",
        period_type="month",
        period_value="8",
        record_type="TX",
        value=41.0,
        date=dt.date(2019, 8, 10),
        department=76,
    )
    # all_time : ne doit pas être compté avec period_type=month
    insert_mv_record(
        station_code="76116010",
        station_name="Station All Time",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=40.0,
        date=dt.date(2019, 7, 25),
        department=76,
    )

    ds = TimescaleRecordsGraphDataSource()
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
    assert bucket_2019.nb_records_battus == 2  # juillet + août, pas all_time


@pytest.mark.django_db
def test_fetch_graph_period_type_season_all_seasons():
    insert_mv_record(
        station_code="76116011",
        station_name="Station Été",
        period_type="season",
        period_value="summer",
        record_type="TX",
        value=43.0,
        date=dt.date(2019, 7, 25),
        department=76,
    )
    insert_mv_record(
        station_code="76116012",
        station_name="Station Printemps",
        period_type="season",
        period_value="spring",
        record_type="TX",
        value=30.0,
        date=dt.date(2019, 4, 15),
        department=76,
    )
    # all_time : ne doit pas être compté avec period_type=season
    insert_mv_record(
        station_code="76116013",
        station_name="Station All Time",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=40.0,
        date=dt.date(2019, 6, 1),
        department=76,
    )

    ds = TimescaleRecordsGraphDataSource()
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
    assert bucket_2019.nb_records_battus == 2  # summer + spring, pas all_time


@pytest.mark.django_db
def test_fetch_graph_period_type_month_specific_excludes_other_months():
    insert_mv_record(
        station_code="76116014",
        station_name="Station Juillet",
        period_type="month",
        period_value="7",
        record_type="TX",
        value=43.0,
        date=dt.date(2019, 7, 25),
        department=76,
    )
    insert_mv_record(
        station_code="76116015",
        station_name="Station Août",
        period_type="month",
        period_value="8",
        record_type="TX",
        value=41.0,
        date=dt.date(2019, 8, 10),
        department=76,
    )

    ds = TimescaleRecordsGraphDataSource()
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
    assert bucket_2019.nb_records_battus == 1  # juillet uniquement
