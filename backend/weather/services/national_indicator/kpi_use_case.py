from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from statistics import mean

from weather.services.national_indicator.protocols import (
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.types import DailySeriesQuery


@dataclass(frozen=True)
class KpiPeriodStats:
    hot_peak_count: int
    cold_peak_count: int
    days_above_baseline: int
    days_below_baseline: int
    itn_mean: float | None
    deviation_from_normal: float | None


@dataclass(frozen=True)
class NationalIndicatorKpiResult:
    current: KpiPeriodStats
    previous: KpiPeriodStats


def _compute_period_stats(
    observed_data_source: NationalIndicatorObservedDataSource,
    baseline_data_source: NationalIndicatorBaselineDataSource,
    date_start: dt.date,
    date_end: dt.date,
) -> KpiPeriodStats:
    observed = observed_data_source.fetch_daily_series(
        DailySeriesQuery(date_start=date_start, date_end=date_end)
    )

    hot_peak_count = 0
    cold_peak_count = 0
    days_above_baseline = 0
    days_below_baseline = 0
    baseline_means: list[float] = []

    for point in observed:
        baseline = baseline_data_source.fetch_daily_baseline(point.date)
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


def get_national_indicator_kpi(
    *,
    observed_data_source: NationalIndicatorObservedDataSource,
    baseline_data_source: NationalIndicatorBaselineDataSource,
    date_start: dt.date,
    date_end: dt.date,
) -> NationalIndicatorKpiResult:
    duration = date_end - date_start
    prev_date_end = date_start - dt.timedelta(days=1)
    prev_date_start = prev_date_end - duration

    current = _compute_period_stats(
        observed_data_source, baseline_data_source, date_start, date_end
    )
    previous = _compute_period_stats(
        observed_data_source, baseline_data_source, prev_date_start, prev_date_end
    )

    return NationalIndicatorKpiResult(current=current, previous=previous)
