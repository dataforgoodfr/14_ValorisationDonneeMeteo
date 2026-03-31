from __future__ import annotations

from typing import Protocol

from .types import (
    DailyBaselinePoint,
    DailyDeviationSeriesQuery,
    MonthlyBaselinePoint,
    ObservedPoint,
    StationDailySeries,
    YearlyBaselinePoint,
)


class TemperatureDeviationDailyDataSource(Protocol):
    def fetch_national_observed_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[ObservedPoint]:
        """
        Retourne la température nationale observée (ITN) uniquement.
        La baseline est injectée après agrégation dans le service.
        """

    def fetch_national_daily_baseline(self) -> list[DailyBaselinePoint]:
        """
        Retourne la climatologie journalière ITN (baseline 1991-2020).
        """

    def fetch_national_monthly_baseline(self) -> list[MonthlyBaselinePoint]:
        """
        Retourne la climatologie mensuelle ITN (baseline 1991-2020).
        """

    def fetch_national_yearly_baseline(self) -> YearlyBaselinePoint | None:
        """
        Retourne la climatologie annuelle ITN (baseline 1991-2020).
        """

    def fetch_stations_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[StationDailySeries]:
        """
        Retourne les séries journalières par station, avec baseline déjà jointe.
        """
