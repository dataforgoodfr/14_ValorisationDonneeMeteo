from __future__ import annotations

import datetime as dt

from weather.utils.date_range import (
    days_in_month_in_range,
    monthly_points_in_range,
    yearly_points_in_range,
)

from .aggregation import aggregate_observed
from .protocols import (
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from .slicing import apply_slice
from .source_window import compute_source_window
from .types import DailySeriesQuery, OutputPoint


def compute_target_dates(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str,
    month_of_year: int | None,
    day_of_month: int | None,
) -> tuple[dt.date, ...] | None:
    if slice_type == "full":
        return None

    if slice_type == "month_of_year":
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")

        return days_in_month_in_range(
            date_start=date_start,
            date_end=date_end,
            month=month_of_year,
        )

    if day_of_month is None:
        raise ValueError("day_of_month ne doit pas être None")

    if granularity == "month":
        return monthly_points_in_range(
            date_start=date_start,
            date_end=date_end,
            day_of_month=day_of_month,
        )

    if granularity == "year":
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")

        return yearly_points_in_range(
            date_start=date_start,
            date_end=date_end,
            month=month_of_year,
            day_of_month=day_of_month,
        )

    raise ValueError(
        f"Combinaison invalide granularity={granularity}, slice_type={slice_type}"
    )


def _baseline_for_output_point(
    *,
    point_date: dt.date,
    granularity: str,
    slice_type: str,
    baseline_data_source: NationalIndicatorBaselineDataSource,
):
    if granularity == "day":
        return baseline_data_source.fetch_daily_baseline(point_date)

    if granularity == "month":
        if slice_type == "full":
            return baseline_data_source.fetch_monthly_baseline(point_date.month)
        if slice_type == "day_of_month":
            return baseline_data_source.fetch_daily_baseline(point_date)

    if granularity == "year":
        if slice_type == "full":
            return baseline_data_source.fetch_yearly_baseline()
        if slice_type == "month_of_year":
            return baseline_data_source.fetch_monthly_baseline(point_date.month)
        if slice_type == "day_of_month":
            return baseline_data_source.fetch_daily_baseline(point_date)

    raise ValueError(
        f"Combinaison invalide granularity={granularity}, slice_type={slice_type}"
    )


def compute_national_indicator(
    *,
    observed_data_source: NationalIndicatorObservedDataSource,
    baseline_data_source: NationalIndicatorBaselineDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str = "full",
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> dict:
    # 1. Fenêtre source
    src_start, src_end = compute_source_window(
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
    )

    # 2. Target dates
    target_dates = compute_target_dates(
        date_start=src_start,
        date_end=src_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )

    # 3. Query
    query = DailySeriesQuery(
        date_start=src_start,
        date_end=src_end,
        target_dates=target_dates,
    )

    # 4. Fetch observé journalier
    daily = observed_data_source.fetch_daily_series(query)

    # 5. Slice
    sliced = apply_slice(
        daily,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )

    # 6. Agrégation observée
    observed_points = aggregate_observed(
        sliced,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
    )

    # 7. Enrichissement baseline
    points: list[OutputPoint] = []
    for p in observed_points:
        b = _baseline_for_output_point(
            point_date=p.date,
            granularity=granularity,
            slice_type=slice_type,
            baseline_data_source=baseline_data_source,
        )

        points.append(
            OutputPoint(
                date=p.date,
                temperature=p.temperature,
                baseline_mean=b.baseline_mean,
                baseline_std_dev_upper=b.baseline_std_dev_upper,
                baseline_std_dev_lower=b.baseline_std_dev_lower,
                baseline_max=b.baseline_max,
                baseline_min=b.baseline_min,
            )
        )

    # 8. Format réponse
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
