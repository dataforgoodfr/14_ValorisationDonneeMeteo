from __future__ import annotations

import datetime as dt
from typing import Protocol

from .types import (
    AbsoluteExtremes,
    BaselinePoint,
    DailySeriesQuery,
    NationalIndicatorKpiResult,
    ObservedPoint,
)


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


class NationalIndicatorAbsoluteExtremesDataSource(Protocol):
    """
    Source des extremes absolus historiques de l'ITN (1947 à aujourd'hui).
    Les résultats ne dépendent pas de la fenêtre date_start/date_end de la requête.
    """

    def fetch_daily_absolute_extremes(
        self,
        month_day_pairs: set[tuple[int, int]],
    ) -> dict[tuple[int, int], AbsoluteExtremes]:
        """
        Pour chaque (mois, jour) demandé, retourne le min/max de l'ITN journalier
        observé sur tous les années disponibles pour ce même (mois, jour).
        """
        ...

    def fetch_monthly_absolute_extremes(
        self,
        months: set[int],
    ) -> dict[int, AbsoluteExtremes]:
        """
        Pour chaque mois demandé, retourne le min/max de la moyenne mensuelle de l'ITN
        observée sur toutes les années disponibles pour ce mois.
        """
        ...

    def fetch_yearly_absolute_extremes(self) -> AbsoluteExtremes:
        """
        Retourne le min/max de la moyenne annuelle de l'ITN
        observée sur toutes les années disponibles.
        """
        ...


class NationalIndicatorKpiDataSource(Protocol):
    """
    Chemin rapide : calcule en une seule requête SQL les KPI ITN
    pour la période courante et la période précédente.
    """

    def compute_kpi(
        self,
        *,
        current_start: dt.date,
        current_end: dt.date,
        previous_start: dt.date,
        previous_end: dt.date,
    ) -> NationalIndicatorKpiResult: ...
