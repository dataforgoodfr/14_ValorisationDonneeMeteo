from __future__ import annotations

from typing import Protocol

from .types import (
    DailyMinMaxPoint,
    MinMaxGraphQuery,
    MinMaxOverviewQuery,
    MinMaxOverviewResult,
    StationDailyMinMaxSeries,
)


class MinMaxGraphDataSource(Protocol):
    def fetch_daily_series(
        self, query: MinMaxGraphQuery
    ) -> list[StationDailyMinMaxSeries]: ...

    def fetch_national_daily_series(
        self, query: MinMaxGraphQuery
    ) -> list[DailyMinMaxPoint]: ...


class MinMaxOverviewDataSource(Protocol):
    def fetch_station_overview(
        self, query: MinMaxOverviewQuery
    ) -> MinMaxOverviewResult: ...
