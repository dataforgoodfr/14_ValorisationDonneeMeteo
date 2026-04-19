import datetime as dt

from weather.utils.date_range import (
    iter_month_starts_intersecting,
    iter_year_starts_intersecting,
)

from .types import (
    AggregatedDeviationPoint,
    DailyDeviationPoint,
    ObservedPoint,
)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def aggregate_observed(
    points: list[ObservedPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str,
    month_of_year: int | None = None,
) -> list[ObservedPoint]:
    """
    Agrégation nationale (température seule).
    """

    if granularity == "day":
        return points

    # cas slicing déjà 1 point / bucket
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

            out.append(
                ObservedPoint(
                    date=dt.date(y, m, 1),
                    temperature=_mean([p.temperature for p in bucket]),
                )
            )
        return out

    # year
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

        out.append(
            ObservedPoint(
                date=anchor,
                temperature=_mean([p.temperature for p in bucket]),
            )
        )

    return out


def aggregate_station_daily(
    points: list[DailyDeviationPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str,
    month_of_year: int | None = None,
) -> list[AggregatedDeviationPoint]:
    """
    Agrégation station avec baseline.
    """

    if granularity == "day":
        return [
            AggregatedDeviationPoint(
                date=p.date,
                temperature=p.temperature,
                baseline_mean=p.baseline_mean,
            )
            for p in points
        ]

    # slicing => déjà 1 point par bucket
    if granularity == "month" and slice_type == "day_of_month":
        return [
            AggregatedDeviationPoint(
                date=p.date,
                temperature=p.temperature,
                baseline_mean=p.baseline_mean,
            )
            for p in points
        ]

    if granularity == "year" and slice_type == "day_of_month":
        return [
            AggregatedDeviationPoint(
                date=p.date,
                temperature=p.temperature,
                baseline_mean=p.baseline_mean,
            )
            for p in points
        ]

    if granularity == "month":
        out: list[AggregatedDeviationPoint] = []
        for month_start in iter_month_starts_intersecting(date_start, date_end):
            y, m = month_start.year, month_start.month
            bucket = [p for p in points if p.date.year == y and p.date.month == m]
            if not bucket:
                continue

            out.append(
                AggregatedDeviationPoint(
                    date=dt.date(y, m, 1),
                    temperature=_mean([p.temperature for p in bucket]),
                    baseline_mean=_mean([p.baseline_mean for p in bucket]),
                )
            )
        return out

    # year
    out: list[AggregatedDeviationPoint] = []
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

        out.append(
            AggregatedDeviationPoint(
                date=anchor,
                temperature=_mean([p.temperature for p in bucket]),
                baseline_mean=_mean([p.baseline_mean for p in bucket]),
            )
        )

    return out
