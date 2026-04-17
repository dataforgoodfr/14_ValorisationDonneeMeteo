from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

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
    days: list[KpiDay]
    count: int


def get_national_indicator_kpi(
    *,
    observed_data_source: NationalIndicatorObservedDataSource,
    baseline_data_source: NationalIndicatorBaselineDataSource,
    date_start: dt.date,
    date_end: dt.date,
    peak_type: str,
) -> NationalIndicatorKpiResult:
    observed = observed_data_source.fetch_daily_series(
        DailySeriesQuery(date_start=date_start, date_end=date_end)
    )

    peak_days: list[KpiDay] = []

    for point in observed:
        baseline = baseline_data_source.fetch_daily_baseline(point.date)

        std_dev = baseline.baseline_std_dev_upper - baseline.baseline_mean

        if peak_type == "hot" and point.temperature > baseline.baseline_std_dev_upper:
            peak_days.append(
                KpiDay(
                    date=point.date,
                    temperature=point.temperature,
                    baseline_mean=baseline.baseline_mean,
                    baseline_std_dev=std_dev,
                )
            )
        elif (
            peak_type == "cold" and point.temperature < baseline.baseline_std_dev_lower
        ):
            peak_days.append(
                KpiDay(
                    date=point.date,
                    temperature=point.temperature,
                    baseline_mean=baseline.baseline_mean,
                    baseline_std_dev=std_dev,
                )
            )

    return NationalIndicatorKpiResult(days=peak_days, count=len(peak_days))
