"""
Fake datasource pour l'ITN.

IMPORTANT:
Ce fake n'est PAS statistiquement rigoureux.

- Les baselines monthly/yearly sont dérivées de moyennes de statistiques journalières.
- Les écarts-types ne sont PAS recalculés correctement (pas de prise en compte des covariances).
- Le but est uniquement de fournir des données plausibles pour tests / démo.

NE PAS utiliser comme référence scientifique.
"""

from __future__ import annotations

import datetime as dt
import math
import random
from statistics import mean

from weather.services.national_indicator.protocols import (
    NationalIndicatorAbsoluteExtremesDataSource,
    NationalIndicatorBaselineDataSource,
    NationalIndicatorKpiDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.service import compute_national_indicator
from weather.services.national_indicator.types import (
    AbsoluteExtremes,
    BaselinePoint,
    DailySeriesQuery,
    KpiPeriodStats,
    NationalIndicatorKpiResult,
    ObservedPoint,
)
from weather.utils.date_range import iter_days_intersecting


def _climatology_for_date(d: dt.date) -> tuple[float, float]:
    """
    Retourne une climatologie synthétique pour une date donnée :
    (mean, stddev, min, max)
    """
    doy = d.timetuple().tm_yday
    phi = 2.0 * math.pi * (doy - 15) / 365.25

    mean_annual = 13.0
    amplitude = 6.0
    baseline_mean = mean_annual + amplitude * math.sin(phi)

    sigma_base = 1.6
    sigma_amp = 0.6
    sigma = sigma_base + sigma_amp * (1 - math.sin(phi)) / 2.0

    return baseline_mean, sigma


def _baseline_point_from_mean_std(
    *,
    mean: float,
    stddev: float,
) -> BaselinePoint:
    return BaselinePoint(
        baseline_mean=mean,
        baseline_std_dev_upper=mean + stddev,
        baseline_std_dev_lower=mean - stddev,
    )


class FakeNationalIndicatorDataSource(
    NationalIndicatorObservedDataSource,
    NationalIndicatorBaselineDataSource,
):
    def __init__(self, *, seed: int = 42) -> None:
        self._seed = seed

    def fetch_daily_series(
        self,
        query: DailySeriesQuery,
    ) -> list[ObservedPoint]:
        rng = random.Random(self._seed)
        out: list[ObservedPoint] = []

        days: tuple[dt.date, ...]
        if query.target_dates is not None:
            days = query.target_dates
        else:
            days = tuple(iter_days_intersecting(query.date_start, query.date_end))

        for d in days:
            baseline_mean, sigma = _climatology_for_date(d)
            temperature = baseline_mean + rng.gauss(0.0, sigma)
            out.append(
                ObservedPoint(
                    date=d,
                    temperature=temperature,
                )
            )

        return out

    def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
        mean, stddev = _climatology_for_date(day)
        return _baseline_point_from_mean_std(mean=mean, stddev=stddev)

    def fetch_monthly_baseline(self, month: int) -> BaselinePoint:
        """
        Baseline mensuelle APPROXIMATIVE.

        IMPORTANT:
        - L'écart-type est calculé comme moyenne des std journaliers.
        - Ceci est statistiquement faux (pas de reconstruction des séries mensuelles).
        - Pas de prise en compte des covariances inter-jours.

        Accepté ici uniquement pour un fake.
        """
        ref_days = [dt.date(2001, month, day) for day in range(1, 29)]
        daily_stats = [_climatology_for_date(d) for d in ref_days]

        mean = sum(s[0] for s in daily_stats) / len(daily_stats)
        stddev = sum(s[1] for s in daily_stats) / len(daily_stats)

        return _baseline_point_from_mean_std(mean=mean, stddev=stddev)

    def fetch_yearly_baseline(self) -> BaselinePoint:
        """
        Baseline annuelle APPROXIMATIVE.

        IMPORTANT:
        - Même limitation que pour le mensuel.
        - L'écart-type annuel n'est PAS celui d'une vraie distribution annuelle.

        Suffisant pour tests, mais pas pour validation métier.
        """
        ref_days = [dt.date(2001, 1, 1) + dt.timedelta(days=i) for i in range(365)]
        daily_stats = [_climatology_for_date(d) for d in ref_days]

        mean = sum(s[0] for s in daily_stats) / len(daily_stats)
        stddev = sum(s[1] for s in daily_stats) / len(daily_stats)

        return _baseline_point_from_mean_std(mean=mean, stddev=stddev)


def _absolute_extremes_for_day(month: int, day_of_month: int) -> AbsoluteExtremes:
    """
    Extremes absolus synthétiques pour un (mois, jour) donné.
    Dérivés de la climatologie en simulant une dispersion autour de la moyenne.
    """
    ref = dt.date(2001, month, min(day_of_month, 28))
    mean, sigma = _climatology_for_date(ref)
    return AbsoluteExtremes(
        absolute_min=round(mean - sigma, 4),
        absolute_max=round(mean + sigma, 4),
    )


class FakeNationalIndicatorAbsoluteExtremesDataSource(
    NationalIndicatorAbsoluteExtremesDataSource,
):
    """
    Fake implémentation des extremes absolus pour tests et démo.
    Les valeurs sont synthétiques, dérivées de la même climatologie que FakeNationalIndicatorDataSource.
    """

    def fetch_daily_absolute_extremes(
        self,
        month_day_pairs: set[tuple[int, int]],
    ) -> dict[tuple[int, int], AbsoluteExtremes]:
        return {(m, d): _absolute_extremes_for_day(m, d) for m, d in month_day_pairs}

    def fetch_monthly_absolute_extremes(
        self,
        months: set[int],
    ) -> dict[int, AbsoluteExtremes]:
        result: dict[int, AbsoluteExtremes] = {}
        for month in months:
            ref_days = [dt.date(2001, month, day) for day in range(1, 29)]
            mins = [
                _climatology_for_date(d)[0] - _climatology_for_date(d)[1]
                for d in ref_days
            ]
            maxs = [
                _climatology_for_date(d)[0] + _climatology_for_date(d)[1]
                for d in ref_days
            ]
            result[month] = AbsoluteExtremes(
                absolute_min=round(min(mins), 4),
                absolute_max=round(max(maxs), 4),
            )
        return result

    def fetch_yearly_absolute_extremes(self) -> AbsoluteExtremes:
        ref_days = [dt.date(2001, 1, 1) + dt.timedelta(days=i) for i in range(365)]
        mins = [
            _climatology_for_date(d)[0] - _climatology_for_date(d)[1] for d in ref_days
        ]
        maxs = [
            _climatology_for_date(d)[0] + _climatology_for_date(d)[1] for d in ref_days
        ]
        return AbsoluteExtremes(
            absolute_min=round(min(mins), 4),
            absolute_max=round(max(maxs), 4),
        )


class FakeNationalIndicatorKpiDataSource(NationalIndicatorKpiDataSource):
    """
    KPI ITN sur données synthétiques : boucle sur l'observé + baseline
    fournis par FakeNationalIndicatorDataSource.
    """

    def __init__(self, *, fake: FakeNationalIndicatorDataSource) -> None:
        self._fake = fake

    def compute_kpi(
        self,
        *,
        current_start: dt.date,
        current_end: dt.date,
        previous_start: dt.date,
        previous_end: dt.date,
    ) -> NationalIndicatorKpiResult:
        return NationalIndicatorKpiResult(
            current=self._period_stats(current_start, current_end),
            previous=self._period_stats(previous_start, previous_end),
        )

    def _period_stats(self, date_start: dt.date, date_end: dt.date) -> KpiPeriodStats:
        observed = self._fake.fetch_daily_series(
            DailySeriesQuery(date_start=date_start, date_end=date_end)
        )

        hot_peak_count = 0
        cold_peak_count = 0
        days_above_baseline = 0
        days_below_baseline = 0
        baseline_means: list[float] = []

        for point in observed:
            baseline = self._fake.fetch_daily_baseline(point.date)
            baseline_means.append(baseline.baseline_mean)

            if point.temperature > baseline.baseline_mean:
                days_above_baseline += 1
            elif point.temperature < baseline.baseline_mean:
                days_below_baseline += 1

            if point.temperature > baseline.baseline_std_dev_upper:
                hot_peak_count += 1
            elif point.temperature < baseline.baseline_std_dev_lower:
                cold_peak_count += 1

        if observed:
            itn_mean = mean(p.temperature for p in observed)
            deviation_from_normal = itn_mean - mean(baseline_means)
        else:
            itn_mean = None
            deviation_from_normal = None

        return KpiPeriodStats(
            hot_peak_count=hot_peak_count,
            cold_peak_count=cold_peak_count,
            days_above_baseline=days_above_baseline,
            days_below_baseline=days_below_baseline,
            itn_mean=itn_mean,
            deviation_from_normal=deviation_from_normal,
        )


def generate_fake_national_indicator(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str = "full",
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> dict:
    """
    Helper pour générer une réponse API complète avec le fake datasource.

    Utilisation:
    - tests
    - debug
    - démonstration

    Ne reflète pas la qualité des données réelles.
    """
    ds = FakeNationalIndicatorDataSource(seed=42)
    extremes_ds = FakeNationalIndicatorAbsoluteExtremesDataSource()
    return compute_national_indicator(
        observed_data_source=ds,
        baseline_data_source=ds,
        absolute_extremes_data_source=extremes_ds,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )
