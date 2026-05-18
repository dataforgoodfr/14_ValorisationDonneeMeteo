from __future__ import annotations

import datetime as dt

from weather.services.temperature_extremes.service import compute_extremes_graph
from weather.services.temperature_extremes.types import (
    DailyExtremesPoint,
    ExtremesGraphQuery,
    StationDailyExtremesSeries,
)


class StubExtremesDataSource:
    def __init__(
        self,
        station_series: list[StationDailyExtremesSeries] | None = None,
        national_points: list[DailyExtremesPoint] | None = None,
    ):
        self._station_series = station_series or []
        self._national_points = national_points or []

    def fetch_daily_series(
        self, query: ExtremesGraphQuery
    ) -> list[StationDailyExtremesSeries]:
        return self._station_series

    def fetch_national_daily_series(
        self, query: ExtremesGraphQuery
    ) -> list[DailyExtremesPoint]:
        return self._national_points


def test_without_territoire_filter_returns_national():
    ds = StubExtremesDataSource(
        national_points=[
            DailyExtremesPoint(date=dt.date(2020, 1, 1), tn=-2.0, tx=5.0),
            DailyExtremesPoint(date=dt.date(2020, 1, 2), tn=0.0, tx=7.0),
        ]
    )
    query = ExtremesGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 1, 2),
        granularity="day",
    )

    result = compute_extremes_graph(data_source=ds, query=query)

    assert "national" in result
    assert result["stations"] == []
    assert len(result["national"]["data"]) == 2


def test_with_station_ids_returns_stations():
    ds = StubExtremesDataSource(
        station_series=[
            StationDailyExtremesSeries(
                station_id="07149",
                station_name="Paris",
                points=[DailyExtremesPoint(date=dt.date(2020, 1, 1), tn=-2.0, tx=5.0)],
            )
        ]
    )
    query = ExtremesGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 1, 31),
        granularity="month",
        station_ids=("07149",),
    )

    result = compute_extremes_graph(data_source=ds, query=query)

    assert "national" not in result
    assert len(result["stations"]) == 1
    assert result["stations"][0]["station_id"] == "07149"


def test_with_departments_filter_returns_aggregated_series():
    ds = StubExtremesDataSource(
        national_points=[
            DailyExtremesPoint(date=dt.date(2020, 1, 1), tn=-2.0, tx=5.0),
        ]
    )
    query = ExtremesGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 1, 31),
        granularity="month",
        departments=("75",),
    )

    result = compute_extremes_graph(data_source=ds, query=query)

    assert "national" in result
    assert result["stations"] == []


def test_aggregation_granularity_month():
    ds = StubExtremesDataSource(
        national_points=[
            DailyExtremesPoint(date=dt.date(2020, 1, 1), tn=-2.0, tx=5.0),
            DailyExtremesPoint(date=dt.date(2020, 1, 15), tn=0.0, tx=9.0),
            DailyExtremesPoint(date=dt.date(2020, 2, 1), tn=1.0, tx=11.0),
        ]
    )
    query = ExtremesGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 2, 28),
        granularity="month",
    )

    result = compute_extremes_graph(data_source=ds, query=query)

    data = result["national"]["data"]
    assert len(data) == 2
    assert data[0]["date"] == dt.date(2020, 1, 1)
    assert data[0]["tn_mean"] == -1.0
    assert data[0]["tx_mean"] == 7.0


def test_aggregation_granularity_year():
    ds = StubExtremesDataSource(
        national_points=[
            DailyExtremesPoint(date=dt.date(2020, 1, 1), tn=-2.0, tx=5.0),
            DailyExtremesPoint(date=dt.date(2020, 6, 15), tn=14.0, tx=28.0),
            DailyExtremesPoint(date=dt.date(2021, 3, 1), tn=3.0, tx=12.0),
        ]
    )
    query = ExtremesGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2021, 12, 31),
        granularity="year",
    )

    result = compute_extremes_graph(data_source=ds, query=query)

    data = result["national"]["data"]
    assert len(data) == 2
    assert data[0]["date"] == dt.date(2020, 1, 1)
    assert data[0]["tn_mean"] == 6.0
    assert data[0]["tx_mean"] == 16.5


def test_none_values_are_ignored():
    ds = StubExtremesDataSource(
        national_points=[
            DailyExtremesPoint(date=dt.date(2020, 1, 1), tn=None, tx=None),
            DailyExtremesPoint(date=dt.date(2020, 1, 2), tn=-1.0, tx=6.0),
        ]
    )
    query = ExtremesGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 1, 2),
        granularity="day",
    )

    result = compute_extremes_graph(data_source=ds, query=query)

    assert len(result["national"]["data"]) == 1
    assert result["national"]["data"][0]["date"] == dt.date(2020, 1, 2)
