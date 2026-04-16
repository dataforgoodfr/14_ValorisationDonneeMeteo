from __future__ import annotations

import datetime as dt

from weather.services.temperature_minmax.service import compute_minmax_graph
from weather.services.temperature_minmax.types import (
    DailyMinMaxPoint,
    MinMaxGraphQuery,
    StationDailyMinMaxSeries,
)


class StubMinMaxDataSource:
    def __init__(
        self,
        station_series: list[StationDailyMinMaxSeries] | None = None,
        national_points: list[DailyMinMaxPoint] | None = None,
    ):
        self._station_series = station_series or []
        self._national_points = national_points or []

    def fetch_daily_series(
        self, query: MinMaxGraphQuery
    ) -> list[StationDailyMinMaxSeries]:
        return self._station_series

    def fetch_national_daily_series(
        self, query: MinMaxGraphQuery
    ) -> list[DailyMinMaxPoint]:
        return self._national_points


def test_without_territoire_filter_returns_national():
    ds = StubMinMaxDataSource(
        national_points=[
            DailyMinMaxPoint(date=dt.date(2020, 1, 1), tmin=-2.0, tmax=5.0),
            DailyMinMaxPoint(date=dt.date(2020, 1, 2), tmin=0.0, tmax=7.0),
        ]
    )
    query = MinMaxGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 1, 2),
        granularity="day",
    )

    result = compute_minmax_graph(data_source=ds, query=query)

    assert "national" in result
    assert result["stations"] == []
    assert len(result["national"]["data"]) == 2


def test_with_station_ids_returns_stations():
    ds = StubMinMaxDataSource(
        station_series=[
            StationDailyMinMaxSeries(
                station_id="07149",
                station_name="Paris",
                points=[
                    DailyMinMaxPoint(date=dt.date(2020, 1, 1), tmin=-2.0, tmax=5.0)
                ],
            )
        ]
    )
    query = MinMaxGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 1, 31),
        granularity="month",
        station_ids=("07149",),
    )

    result = compute_minmax_graph(data_source=ds, query=query)

    assert "national" not in result
    assert len(result["stations"]) == 1
    assert result["stations"][0]["station_id"] == "07149"


def test_with_departments_filter_returns_stations():
    ds = StubMinMaxDataSource(
        station_series=[
            StationDailyMinMaxSeries(
                station_id="07149",
                station_name="Paris",
                points=[
                    DailyMinMaxPoint(date=dt.date(2020, 1, 1), tmin=-2.0, tmax=5.0)
                ],
            )
        ]
    )
    query = MinMaxGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 1, 31),
        granularity="month",
        departments=("75",),
    )

    result = compute_minmax_graph(data_source=ds, query=query)

    assert "national" not in result
    assert len(result["stations"]) == 1


def test_aggregation_granularity_month():
    ds = StubMinMaxDataSource(
        national_points=[
            DailyMinMaxPoint(date=dt.date(2020, 1, 1), tmin=-2.0, tmax=5.0),
            DailyMinMaxPoint(date=dt.date(2020, 1, 15), tmin=0.0, tmax=9.0),
            DailyMinMaxPoint(date=dt.date(2020, 2, 1), tmin=1.0, tmax=11.0),
        ]
    )
    query = MinMaxGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 2, 28),
        granularity="month",
    )

    result = compute_minmax_graph(data_source=ds, query=query)

    data = result["national"]["data"]
    assert len(data) == 2
    assert data[0]["date"] == dt.date(2020, 1, 1)
    assert data[0]["tmin_mean"] == -1.0
    assert data[0]["tmax_mean"] == 7.0


def test_aggregation_granularity_year():
    ds = StubMinMaxDataSource(
        national_points=[
            DailyMinMaxPoint(date=dt.date(2020, 1, 1), tmin=-2.0, tmax=5.0),
            DailyMinMaxPoint(date=dt.date(2020, 6, 15), tmin=14.0, tmax=28.0),
            DailyMinMaxPoint(date=dt.date(2021, 3, 1), tmin=3.0, tmax=12.0),
        ]
    )
    query = MinMaxGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2021, 12, 31),
        granularity="year",
    )

    result = compute_minmax_graph(data_source=ds, query=query)

    data = result["national"]["data"]
    assert len(data) == 2
    assert data[0]["date"] == dt.date(2020, 1, 1)
    assert data[0]["tmin_mean"] == 6.0
    assert data[0]["tmax_mean"] == 16.5


def test_none_values_are_ignored():
    ds = StubMinMaxDataSource(
        national_points=[
            DailyMinMaxPoint(date=dt.date(2020, 1, 1), tmin=None, tmax=None),
            DailyMinMaxPoint(date=dt.date(2020, 1, 2), tmin=-1.0, tmax=6.0),
        ]
    )
    query = MinMaxGraphQuery(
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2020, 1, 2),
        granularity="day",
    )

    result = compute_minmax_graph(data_source=ds, query=query)

    assert len(result["national"]["data"]) == 1
    assert result["national"]["data"][0]["date"] == dt.date(2020, 1, 2)
