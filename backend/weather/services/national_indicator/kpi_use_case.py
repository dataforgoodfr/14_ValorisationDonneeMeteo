from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from statistics import mean

from weather.services.national_indicator.protocols import (
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.types import BaselinePoint, DailySeriesQuery


@dataclass(frozen=True)
class KpiDay:
    date: dt.date
    temperature: float
    baseline_mean: float
    baseline_std_dev: float


@dataclass(frozen=True)
class NationalIndicatorKpiResult:
    days: list[KpiDay]
    count: int
    itn_mean: float | None
    deviation_from_normal: float | None


def is_peak(temperature: float, baseline: BaselinePoint, peak_type: str) -> bool:
    if peak_type == "hot":
        return temperature > baseline.baseline_std_dev_upper
    return temperature < baseline.baseline_std_dev_lower


def get_national_indicator_kpi(
    *,
    observed_data_source: NationalIndicatorObservedDataSource,
    baseline_data_source: NationalIndicatorBaselineDataSource,
    date_start: dt.date,
    date_end: dt.date,
    peak_type: str | None,
) -> NationalIndicatorKpiResult:
    observed = observed_data_source.fetch_daily_series(
        DailySeriesQuery(date_start=date_start, date_end=date_end)
    )

    peak_days: list[KpiDay] = []
    baseline_means: list[float] = []

    for point in observed:
        baseline = baseline_data_source.fetch_daily_baseline(point.date)

        std_dev = baseline.baseline_std_dev_upper - baseline.baseline_mean
        baseline_means.append(baseline.baseline_mean)

        if peak_type is not None and is_peak(point.temperature, baseline, peak_type):
            peak_days.append(
                KpiDay(
                    date=point.date,
                    temperature=point.temperature,
                    baseline_mean=baseline.baseline_mean,
                    baseline_std_dev=std_dev,
                )
            )

    if observed:
        itn_mean = mean(p.temperature for p in observed)
        baseline_period_mean = mean(baseline_means)
        deviation_from_normal = itn_mean - baseline_period_mean
    else:
        itn_mean = None
        deviation_from_normal = None

    return NationalIndicatorKpiResult(
        days=peak_days,
        count=len(peak_days),
        itn_mean=itn_mean,
        deviation_from_normal=deviation_from_normal,
    )
