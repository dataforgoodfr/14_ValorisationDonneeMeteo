from __future__ import annotations

import datetime as dt

from weather.data_sources.records_graph_fake import FakeRecordsGraphDataSource
from weather.services.records_graph.types import RecordsGraphRequest
from weather.services.records_graph.use_case import get_records_graph


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


def test_records_graph_acceptance_result_has_buckets_and_records():
    ds = FakeRecordsGraphDataSource()
    result = get_records_graph(request=_req(), data_source=ds)

    assert hasattr(result, "buckets")
    assert hasattr(result, "records")
    assert isinstance(result.buckets, list)
    assert isinstance(result.records, list)


def test_records_graph_acceptance_year_granularity_bucket_keys_are_years():
    ds = FakeRecordsGraphDataSource()
    result = get_records_graph(
        request=_req(
            date_start=dt.date(2020, 1, 1),
            date_end=dt.date(2022, 12, 31),
            granularity="year",
        ),
        data_source=ds,
    )

    assert len(result.buckets) == 3
    assert [b.bucket for b in result.buckets] == ["2020", "2021", "2022"]


def test_records_graph_acceptance_all_buckets_present_even_empty_ones():
    ds = FakeRecordsGraphDataSource()
    result = get_records_graph(
        request=_req(
            date_start=dt.date(2050, 1, 1),
            date_end=dt.date(2052, 12, 31),
            granularity="year",
        ),
        data_source=ds,
    )

    assert len(result.buckets) == 3
    assert all(b.nb_records_battus == 0 for b in result.buckets)


def test_records_graph_acceptance_hot_type_records_only_contains_hot():
    ds = FakeRecordsGraphDataSource()
    result = get_records_graph(request=_req(type_records="hot"), data_source=ds)

    assert all(r.type_records == "hot" for r in result.records)


def test_records_graph_acceptance_cold_type_records_only_contains_cold():
    ds = FakeRecordsGraphDataSource()
    result = get_records_graph(request=_req(type_records="cold"), data_source=ds)

    assert all(r.type_records == "cold" for r in result.records)


def test_records_graph_acceptance_all_type_records_contains_both():
    ds = FakeRecordsGraphDataSource()
    result = get_records_graph(request=_req(type_records="all"), data_source=ds)

    types = {r.type_records for r in result.records}
    assert "hot" in types
    assert "cold" in types


def test_records_graph_acceptance_records_within_date_range():
    ds = FakeRecordsGraphDataSource()
    date_start = dt.date(2000, 1, 1)
    date_end = dt.date(2005, 12, 31)
    result = get_records_graph(
        request=_req(date_start=date_start, date_end=date_end, type_records="all"),
        data_source=ds,
    )

    for r in result.records:
        assert date_start <= r.date <= date_end


def test_records_graph_acceptance_month_granularity_bucket_keys_are_year_month():
    ds = FakeRecordsGraphDataSource()
    result = get_records_graph(
        request=_req(
            date_start=dt.date(2024, 1, 1),
            date_end=dt.date(2024, 3, 31),
            granularity="month",
        ),
        data_source=ds,
    )

    assert len(result.buckets) == 3
    assert [b.bucket for b in result.buckets] == ["2024-01", "2024-02", "2024-03"]
