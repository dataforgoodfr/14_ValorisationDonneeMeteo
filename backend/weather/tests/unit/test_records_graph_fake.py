from __future__ import annotations

import datetime as dt

from weather.data_sources.records_graph_fake import FakeRecordsGraphDataSource
from weather.services.records_graph.types import RecordsGraphRequest


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


def test_fake_records_graph_hot_returns_non_empty_buckets():
    ds = FakeRecordsGraphDataSource()
    result = ds.fetch_graph(_req(type_records="hot"))

    assert len(result.buckets) >= 1
    total = sum(b.nb_records_battus for b in result.buckets)
    assert total >= 1


def test_fake_records_graph_cold_returns_non_empty_buckets():
    ds = FakeRecordsGraphDataSource()
    result = ds.fetch_graph(_req(type_records="cold"))

    assert len(result.buckets) >= 1
    total = sum(b.nb_records_battus for b in result.buckets)
    assert total >= 1


def test_fake_records_graph_all_returns_both_types():
    ds = FakeRecordsGraphDataSource()
    result = ds.fetch_graph(_req(type_records="all"))

    types = {r.type_records for r in result.records}
    assert "hot" in types
    assert "cold" in types


def test_fake_records_graph_hot_records_are_all_hot():
    ds = FakeRecordsGraphDataSource()
    result = ds.fetch_graph(_req(type_records="hot"))

    assert all(r.type_records == "hot" for r in result.records)


def test_fake_records_graph_cold_records_are_all_cold():
    ds = FakeRecordsGraphDataSource()
    result = ds.fetch_graph(_req(type_records="cold"))

    assert all(r.type_records == "cold" for r in result.records)


def test_fake_records_graph_buckets_cover_full_year_range():
    ds = FakeRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2020, 1, 1),
            date_end=dt.date(2022, 12, 31),
            granularity="year",
        )
    )

    bucket_keys = [b.bucket for b in result.buckets]
    assert "2020" in bucket_keys
    assert "2021" in bucket_keys
    assert "2022" in bucket_keys


def test_fake_records_graph_records_have_correct_shape():
    ds = FakeRecordsGraphDataSource()
    result = ds.fetch_graph(_req(type_records="all"))

    for r in result.records:
        assert isinstance(r.date, dt.date)
        assert isinstance(r.station_id, str)
        assert isinstance(r.station_name, str)
        assert r.type_records in ("hot", "cold")
        assert isinstance(r.valeur, float)


def test_fake_records_graph_is_deterministic():
    ds = FakeRecordsGraphDataSource()
    req = _req(type_records="all")

    r1 = ds.fetch_graph(req)
    r2 = ds.fetch_graph(req)

    assert r1 == r2


def test_fake_records_graph_nb_records_matches_individual_records():
    ds = FakeRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(1940, 1, 1),
            date_end=dt.date(2025, 12, 31),
            granularity="year",
            type_records="all",
        )
    )

    total_from_buckets = sum(b.nb_records_battus for b in result.buckets)
    assert total_from_buckets == len(result.records)
