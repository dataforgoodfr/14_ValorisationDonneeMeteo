from __future__ import annotations

import datetime as dt

from .aggregation import aggregate
from .protocols import NationalIndicatorDailyDataSource
from .slicing import apply_slice
from .source_window import compute_source_window


def compute_national_indicator(
    *,
    data_source: NationalIndicatorDailyDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str = "full",
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> dict:
    # 1) fenêtre source (peut s'élargir pour certains cas annuels ciblés)
    src_start, src_end = compute_source_window(
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
    )

    # 2) données journalières (source interchangeable)
    daily = data_source.fetch_daily_series(
        date_start=src_start,
        date_end=src_end,
    )

    # 3) slice
    sliced = apply_slice(
        daily,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )

    # 4) agrégation (fenêtre logique de requête)
    points = aggregate(
        sliced,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
    )

    # 5) shape API (time_series uniquement)
    return {
        "time_series": [
            {
                "date": p.date.isoformat(),
                "temperature": round(p.temperature, 2),
                "baseline_mean": round(p.baseline_mean, 2),
                "baseline_std_dev_upper": round(p.baseline_std_dev_upper, 2),
                "baseline_std_dev_lower": round(p.baseline_std_dev_lower, 2),
                "baseline_max": round(p.baseline_max, 2),
                "baseline_min": round(p.baseline_min, 2),
            }
            for p in points
        ]
    }
