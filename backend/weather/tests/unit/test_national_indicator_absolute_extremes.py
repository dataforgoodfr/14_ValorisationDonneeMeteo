"""
Tests unitaires pour absolute_min / absolute_max dans l'indicateur thermique national.

Ces tests vérifient :
- que compute_national_indicator() propage les extremes absolus dans les output points
- que la bonne méthode du datasource est appelée selon la granularité
- que les valeurs sont correctement affectées à chaque point
"""

from __future__ import annotations

import datetime as dt

from weather.services.national_indicator.protocols import (
    NationalIndicatorAbsoluteExtremesDataSource,
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.service import compute_national_indicator
from weather.services.national_indicator.types import (
    AbsoluteExtremes,
    BaselinePoint,
    DailySeriesQuery,
    ObservedPoint,
)
from weather.utils.date_range import iter_days_intersecting

# ---------------------------------------------------------------------------
# Stubs partagés
# ---------------------------------------------------------------------------


class _FixedObservedSource(NationalIndicatorObservedDataSource):
    def __init__(self, temps: dict[dt.date, float]):
        self._temps = temps

    def fetch_daily_series(self, query: DailySeriesQuery) -> list[ObservedPoint]:
        days = query.target_dates or tuple(
            iter_days_intersecting(query.date_start, query.date_end)
        )
        return [
            ObservedPoint(date=d, temperature=self._temps[d])
            for d in days
            if d in self._temps
        ]


class _FixedBaselineSource(NationalIndicatorBaselineDataSource):
    def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
        return BaselinePoint(
            baseline_mean=10.0,
            baseline_std_dev_upper=12.0,
            baseline_std_dev_lower=8.0,
        )

    def fetch_monthly_baseline(self, month: int) -> BaselinePoint:
        return self.fetch_daily_baseline(dt.date(2025, month, 1))

    def fetch_yearly_baseline(self) -> BaselinePoint:
        return self.fetch_daily_baseline(dt.date(2025, 1, 1))


class _RecordingAbsoluteExtremesSource(NationalIndicatorAbsoluteExtremesDataSource):
    """Stub qui enregistre les appels et retourne des valeurs distinctes par clé."""

    def __init__(self) -> None:
        self.daily_calls: list[set[tuple[int, int]]] = []
        self.monthly_calls: list[set[int]] = []
        self.yearly_calls: int = 0

    def fetch_daily_absolute_extremes(
        self, month_day_pairs: set[tuple[int, int]]
    ) -> dict[tuple[int, int], AbsoluteExtremes]:
        self.daily_calls.append(month_day_pairs)
        # Valeur unique par (mois, jour) pour vérifier l'affectation correcte
        return {
            (m, d): AbsoluteExtremes(
                absolute_min=float(-m * 100 - d),
                absolute_max=float(m * 100 + d),
            )
            for m, d in month_day_pairs
        }

    def fetch_monthly_absolute_extremes(
        self, months: set[int]
    ) -> dict[int, AbsoluteExtremes]:
        self.monthly_calls.append(months)
        return {
            m: AbsoluteExtremes(absolute_min=float(-m * 10), absolute_max=float(m * 10))
            for m in months
        }

    def fetch_yearly_absolute_extremes(self) -> AbsoluteExtremes:
        self.yearly_calls += 1
        return AbsoluteExtremes(absolute_min=-999.0, absolute_max=999.0)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(
    observed: NationalIndicatorObservedDataSource,
    extremes: NationalIndicatorAbsoluteExtremesDataSource,
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str = "full",
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> list[dict]:
    baseline = _FixedBaselineSource()
    res = compute_national_indicator(
        observed_data_source=observed,
        baseline_data_source=baseline,
        absolute_extremes_data_source=extremes,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )
    return res["time_series"]


# ---------------------------------------------------------------------------
# granularity=day — appel fetch_daily_absolute_extremes
# ---------------------------------------------------------------------------


def test_daily_absolute_extremes_present_in_output():
    day = dt.date(2025, 3, 15)
    observed = _FixedObservedSource({day: 10.0})
    extremes = _RecordingAbsoluteExtremesSource()

    ts = _run(observed, extremes, date_start=day, date_end=day, granularity="day")

    assert len(ts) == 1
    assert "baseline_min" in ts[0]
    assert "baseline_max" in ts[0]


def test_daily_absolute_extremes_uses_daily_method():
    day = dt.date(2025, 3, 15)
    observed = _FixedObservedSource({day: 10.0})
    extremes = _RecordingAbsoluteExtremesSource()

    _run(observed, extremes, date_start=day, date_end=day, granularity="day")

    assert len(extremes.daily_calls) == 1
    assert extremes.monthly_calls == []
    assert extremes.yearly_calls == 0


def test_daily_absolute_extremes_correct_key_lookup():
    day = dt.date(2025, 3, 15)  # month=3, day=15
    observed = _FixedObservedSource({day: 10.0})
    extremes = _RecordingAbsoluteExtremesSource()

    ts = _run(observed, extremes, date_start=day, date_end=day, granularity="day")

    # _RecordingAbsoluteExtremesSource: absolute_min = -(3*100+15) = -315, absolute_max = 315
    assert ts[0]["baseline_min"] == -315.0
    assert ts[0]["baseline_max"] == 315.0


def test_daily_absolute_extremes_different_days_get_different_values():
    day1 = dt.date(2025, 1, 5)  # (1, 5) => min=-105, max=105
    day2 = dt.date(2025, 2, 10)  # (2, 10) => min=-210, max=210
    observed = _FixedObservedSource({day1: 10.0, day2: 10.0})
    extremes = _RecordingAbsoluteExtremesSource()

    ts = _run(observed, extremes, date_start=day1, date_end=day2, granularity="day")

    assert len(ts) == 2
    pts = {p["date"]: p for p in ts}
    assert pts[day1.isoformat()]["baseline_min"] == -105.0
    assert pts[day1.isoformat()]["baseline_max"] == 105.0
    assert pts[day2.isoformat()]["baseline_min"] == -210.0
    assert pts[day2.isoformat()]["baseline_max"] == 210.0


def test_daily_fetch_is_batched_single_call():
    """Un seul appel à fetch_daily_absolute_extremes quelle que soit la taille de la série."""
    days = {dt.date(2025, 1, i): float(i) for i in range(1, 8)}
    observed = _FixedObservedSource(days)
    extremes = _RecordingAbsoluteExtremesSource()

    ts = _run(
        observed,
        extremes,
        date_start=dt.date(2025, 1, 1),
        date_end=dt.date(2025, 1, 7),
        granularity="day",
    )

    assert len(ts) == 7
    # Un seul appel groupé, pas un appel par point
    assert len(extremes.daily_calls) == 1
    assert len(extremes.daily_calls[0]) == 7


# ---------------------------------------------------------------------------
# granularity=month — appel fetch_monthly_absolute_extremes
# ---------------------------------------------------------------------------


def test_monthly_absolute_extremes_uses_monthly_method():
    observed = _FixedObservedSource({dt.date(2025, 1, d): 10.0 for d in range(1, 32)})
    extremes = _RecordingAbsoluteExtremesSource()

    _run(
        observed,
        extremes,
        date_start=dt.date(2025, 1, 1),
        date_end=dt.date(2025, 1, 31),
        granularity="month",
    )

    assert len(extremes.monthly_calls) == 1
    assert extremes.daily_calls == []
    assert extremes.yearly_calls == 0


def test_monthly_absolute_extremes_correct_key_lookup():
    # Mois 1 => min = -10, max = 10
    days = {dt.date(2025, 1, d): 10.0 for d in range(1, 32)}
    observed = _FixedObservedSource(days)
    extremes = _RecordingAbsoluteExtremesSource()

    ts = _run(
        observed,
        extremes,
        date_start=dt.date(2025, 1, 1),
        date_end=dt.date(2025, 1, 31),
        granularity="month",
    )

    assert len(ts) == 1
    assert ts[0]["baseline_min"] == -10.0
    assert ts[0]["baseline_max"] == 10.0


def test_monthly_absolute_extremes_two_months_get_different_values():
    days = {
        **{dt.date(2025, 1, d): 10.0 for d in range(1, 32)},
        **{dt.date(2025, 2, d): 10.0 for d in range(1, 29)},
    }
    observed = _FixedObservedSource(days)
    extremes = _RecordingAbsoluteExtremesSource()

    ts = _run(
        observed,
        extremes,
        date_start=dt.date(2025, 1, 1),
        date_end=dt.date(2025, 2, 28),
        granularity="month",
    )

    assert len(ts) == 2
    pts = {p["date"]: p for p in ts}
    # Mois 1 => -10/10, Mois 2 => -20/20
    assert pts["2025-01-01"]["baseline_min"] == -10.0
    assert pts["2025-01-01"]["baseline_max"] == 10.0
    assert pts["2025-02-01"]["baseline_min"] == -20.0
    assert pts["2025-02-01"]["baseline_max"] == 20.0


# ---------------------------------------------------------------------------
# granularity=year — appel fetch_yearly_absolute_extremes
# ---------------------------------------------------------------------------


def test_yearly_absolute_extremes_uses_yearly_method():
    days = {dt.date(2025, 1, 1) + dt.timedelta(days=i): 10.0 for i in range(365)}
    observed = _FixedObservedSource(days)
    extremes = _RecordingAbsoluteExtremesSource()

    _run(
        observed,
        extremes,
        date_start=dt.date(2025, 1, 1),
        date_end=dt.date(2025, 12, 31),
        granularity="year",
    )

    assert extremes.yearly_calls == 1
    assert extremes.daily_calls == []
    assert extremes.monthly_calls == []


def test_yearly_absolute_extremes_same_value_all_output_points():
    days_2024 = {dt.date(2024, 1, 1) + dt.timedelta(days=i): 10.0 for i in range(366)}
    days_2025 = {dt.date(2025, 1, 1) + dt.timedelta(days=i): 10.0 for i in range(365)}
    observed = _FixedObservedSource({**days_2024, **days_2025})
    extremes = _RecordingAbsoluteExtremesSource()

    ts = _run(
        observed,
        extremes,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2025, 12, 31),
        granularity="year",
    )

    assert len(ts) == 2
    # Les deux années doivent avoir les mêmes valeurs absolues (fetch_yearly_absolute_extremes)
    assert ts[0]["baseline_min"] == ts[1]["baseline_min"] == -999.0
    assert ts[0]["baseline_max"] == ts[1]["baseline_max"] == 999.0
    # Un seul appel, pas un par année
    assert extremes.yearly_calls == 1
