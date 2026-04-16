from __future__ import annotations

from typing import Protocol

from .types import DailyMinMaxPoint, MinMaxGraphQuery, StationDailyMinMaxSeries


class MinMaxGraphDataSource(Protocol):
    def fetch_daily_series(
        self, query: MinMaxGraphQuery
    ) -> list[StationDailyMinMaxSeries]: ...

    def fetch_national_daily_series(
        self, query: MinMaxGraphQuery
    ) -> list[DailyMinMaxPoint]: ...
