from __future__ import annotations

from typing import Protocol

from .types import DailyDeviationPoint, DailyDeviationSeriesQuery, StationDailySeries


class TemperatureDeviationDailyDataSource(Protocol):
    def fetch_national_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[DailyDeviationPoint]:
        """
        National deviation is defined from:
        - observed national temperature = ITN
        - national baseline = mean ITN over baseline period
        """

    def fetch_stations_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[StationDailySeries]: ...
