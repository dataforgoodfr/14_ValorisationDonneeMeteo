import datetime as dt

from weather.services.national_indicator.types import ObservedPoint
from weather.utils.date_range import (
    iter_month_starts_intersecting,
    iter_year_starts_intersecting,
)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _aggregate_bucket(anchor: dt.date, pts: list[ObservedPoint]) -> ObservedPoint:
    return ObservedPoint(
        date=anchor,
        temperature=_mean([p.temperature for p in pts]),
    )


def aggregate_observed(
    points: list[ObservedPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str,
    month_of_year: int | None = None,
) -> list[ObservedPoint]:
    if granularity == "day":
        return points

    if granularity == "month" and slice_type == "day_of_month":
        return points

    if granularity == "year" and slice_type == "day_of_month":
        return points

    if granularity == "month":
        out: list[ObservedPoint] = []
        for month_start in iter_month_starts_intersecting(date_start, date_end):
            y, m = month_start.year, month_start.month
            bucket = [p for p in points if p.date.year == y and p.date.month == m]
            if not bucket:
                continue
            out.append(_aggregate_bucket(dt.date(y, m, 1), bucket))
        return out

    out: list[ObservedPoint] = []
    for year_start in iter_year_starts_intersecting(date_start, date_end):
        y = year_start.year
        bucket = [p for p in points if p.date.year == y]
        if not bucket:
            continue

        if slice_type == "month_of_year":
            if month_of_year is None:
                raise ValueError("month_of_year ne doit pas être None")
            anchor = dt.date(y, month_of_year, 1)
        else:
            anchor = dt.date(y, 1, 1)

        out.append(_aggregate_bucket(anchor, bucket))

    return out
