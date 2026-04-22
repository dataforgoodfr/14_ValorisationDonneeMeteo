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
class KpiDay:
    date: dt.date
    temperature: float
    baseline_mean: float
    baseline_std_dev: float


@dataclass(frozen=True)
class NationalIndicatorKpiResult:
    hot_peak_days: list[KpiDay]
    cold_peak_days: list[KpiDay]
    hot_peak_count: int
    cold_peak_count: int
    days_above_baseline: int
    days_below_baseline: int
    itn_mean: float | None
    deviation_from_normal: float | None


def get_national_indicator_kpi(
    *,
    observed_data_source: NationalIndicatorObservedDataSource,
    baseline_data_source: NationalIndicatorBaselineDataSource,
    date_start: dt.date,
    date_end: dt.date,
) -> NationalIndicatorKpiResult:
    observed = observed_data_source.fetch_daily_series(
        DailySeriesQuery(date_start=date_start, date_end=date_end)
    )

    hot_peak_days: list[KpiDay] = []
    cold_peak_days: list[KpiDay] = []
    baseline_means: list[float] = []
    days_above_baseline = 0
    days_below_baseline = 0

    for point in observed:
        baseline = baseline_data_source.fetch_daily_baseline(point.date)
        std_dev = baseline.baseline_std_dev_upper - baseline.baseline_mean
        baseline_means.append(baseline.baseline_mean)

        if point.temperature > baseline.baseline_mean:
            days_above_baseline += 1
        elif point.temperature < baseline.baseline_mean:
            days_below_baseline += 1

        kpi_day = KpiDay(
            date=point.date,
            temperature=point.temperature,
            baseline_mean=baseline.baseline_mean,
            baseline_std_dev=std_dev,
        )
        if point.temperature > baseline.baseline_std_dev_upper:
            hot_peak_days.append(kpi_day)
        elif point.temperature < baseline.baseline_std_dev_lower:
            cold_peak_days.append(kpi_day)

    if observed:
        itn_mean = mean(p.temperature for p in observed)
        baseline_period_mean = mean(baseline_means)
        deviation_from_normal = itn_mean - baseline_period_mean
    else:
        itn_mean = None
        deviation_from_normal = None

    return NationalIndicatorKpiResult(
        hot_peak_days=hot_peak_days,
        cold_peak_days=cold_peak_days,
        hot_peak_count=len(hot_peak_days),
        cold_peak_count=len(cold_peak_days),
        days_above_baseline=days_above_baseline,
        days_below_baseline=days_below_baseline,
        itn_mean=itn_mean,
        deviation_from_normal=deviation_from_normal,
    )
