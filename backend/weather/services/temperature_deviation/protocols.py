from __future__ import annotations

from typing import Protocol

from .types import DailyDeviationPoint, DailyDeviationSeriesQuery, StationDailySeries


class TemperatureDeviationDailyDataSource(Protocol):
    def fetch_national_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[
        DailyDeviationPoint
    ]: ...  # on verra si y a vraiment un ecart à la normale aggrégé France, j'ai un doute même si les écrans le prévoient

    def fetch_stations_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[StationDailySeries]: ...
