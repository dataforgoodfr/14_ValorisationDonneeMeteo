from __future__ import annotations

import datetime as dt
from typing import Protocol

from .types import BaselinePoint, DailySeriesQuery, ObservedPoint


class NationalIndicatorObservedDataSource(Protocol):
    """
    Source de données journalières observées pour le calcul ITN.
    """

    def fetch_daily_series(
        self,
        query: DailySeriesQuery,
    ) -> list[ObservedPoint]: ...


class NationalIndicatorBaselineDataSource(Protocol):
    """
    Source de climatologie ITN 1991-2020, selon la granularité demandée.
    """

    def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint: ...

    def fetch_monthly_baseline(self, month: int) -> BaselinePoint: ...

    def fetch_yearly_baseline(self) -> BaselinePoint: ...
