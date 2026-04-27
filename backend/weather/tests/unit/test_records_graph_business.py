from __future__ import annotations

import datetime as dt

import pytest

from weather.services.records_graph.types import (
    RecordsGraphBucket,
    RecordsGraphRecord,
    RecordsGraphRequest,
    RecordsGraphResult,
)
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


class ConfigurableRecordsGraphDataSource:
    def __init__(self, result: RecordsGraphResult) -> None:
        self._result = result
        self.last_request: RecordsGraphRequest | None = None

    def fetch_graph(self, request: RecordsGraphRequest) -> RecordsGraphResult:
        self.last_request = request
        return self._result


_EMPTY_RESULT = RecordsGraphResult(buckets=[], records=[])


def test_records_graph_business_returns_datasource_output():
    expected = RecordsGraphResult(
        buckets=[RecordsGraphBucket(bucket="2024", nb_records_battus=3)],
        records=[
            RecordsGraphRecord(
                date=dt.date(2024, 7, 15),
                station_id="07149",
                station_name="Lyon",
                type_records="hot",
                valeur=42.5,
            )
        ],
    )
    ds = ConfigurableRecordsGraphDataSource(expected)

    result = get_records_graph(request=_req(), data_source=ds)

    assert result == expected


def test_records_graph_business_passes_request_to_datasource():
    ds = ConfigurableRecordsGraphDataSource(_EMPTY_RESULT)
    req = _req(granularity="month", type_records="cold")

    get_records_graph(request=req, data_source=ds)

    assert ds.last_request == req


def test_records_graph_business_raises_if_period_type_month_without_month():
    ds = ConfigurableRecordsGraphDataSource(_EMPTY_RESULT)
    req = _req(period_type="month", month=None)

    with pytest.raises(ValueError, match="month"):
        get_records_graph(request=req, data_source=ds)


def test_records_graph_business_raises_if_period_type_season_without_season():
    ds = ConfigurableRecordsGraphDataSource(_EMPTY_RESULT)
    req = _req(period_type="season", season=None)

    with pytest.raises(ValueError, match="season"):
        get_records_graph(request=req, data_source=ds)


def test_records_graph_business_raises_if_date_start_after_date_end():
    ds = ConfigurableRecordsGraphDataSource(_EMPTY_RESULT)
    req = _req(date_start=dt.date(2025, 1, 1), date_end=dt.date(2024, 1, 1))

    with pytest.raises(ValueError, match="date_start"):
        get_records_graph(request=req, data_source=ds)


def test_records_graph_business_period_type_month_with_month_does_not_raise():
    ds = ConfigurableRecordsGraphDataSource(_EMPTY_RESULT)
    req = _req(period_type="month", month=7)

    result = get_records_graph(request=req, data_source=ds)

    assert result == _EMPTY_RESULT


def test_records_graph_business_period_type_season_with_season_does_not_raise():
    ds = ConfigurableRecordsGraphDataSource(_EMPTY_RESULT)
    req = _req(period_type="season", season="summer")

    result = get_records_graph(request=req, data_source=ds)

    assert result == _EMPTY_RESULT


def test_records_graph_business_same_date_start_and_end_does_not_raise():
    ds = ConfigurableRecordsGraphDataSource(_EMPTY_RESULT)
    same = dt.date(2024, 6, 15)
    req = _req(date_start=same, date_end=same)

    result = get_records_graph(request=req, data_source=ds)

    assert result == _EMPTY_RESULT
