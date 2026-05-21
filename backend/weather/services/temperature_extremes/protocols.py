from __future__ import annotations

from typing import Protocol

from .types import (
    DailyExtremesPoint,
    ExtremesGraphQuery,
    ExtremesOverviewQuery,
    ExtremesOverviewResult,
    StationDailyExtremesSeries,
)


class ExtremesGraphDataSource(Protocol):
    def fetch_daily_series(
        self, query: ExtremesGraphQuery
    ) -> list[StationDailyExtremesSeries]: ...

    def fetch_national_daily_series(
        self, query: ExtremesGraphQuery
    ) -> list[DailyExtremesPoint]: ...


class ExtremesOverviewDataSource(Protocol):
    def fetch_station_overview(
        self, query: ExtremesOverviewQuery
    ) -> ExtremesOverviewResult: ...
