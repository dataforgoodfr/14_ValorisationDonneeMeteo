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


def _aggregate_monthly_observed(
    points: list[ObservedPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
) -> list[ObservedPoint]:
    out: list[ObservedPoint] = []

    for month_start in iter_month_starts_intersecting(date_start, date_end):
        year = month_start.year
        month = month_start.month

        bucket = [p for p in points if p.date.year == year and p.date.month == month]
        if not bucket:
            continue

        out.append(
            ObservedPoint(
                date=dt.date(year, month, 1),
                temperature=_mean([p.temperature for p in bucket]),
            )
        )

    return out


def _year_anchor_date(
    *,
    year: int,
    slice_type: str,
    month_of_year: int | None,
) -> dt.date:
    if slice_type == "month_of_year":
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")
        return dt.date(year, month_of_year, 1)

    return dt.date(year, 1, 1)


def _aggregate_yearly_observed(
    points: list[ObservedPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    slice_type: str,
    month_of_year: int | None = None,
) -> list[ObservedPoint]:
    out: list[ObservedPoint] = []

    for year_start in iter_year_starts_intersecting(date_start, date_end):
        year = year_start.year
        bucket = [p for p in points if p.date.year == year]
        if not bucket:
            continue

        anchor = _year_anchor_date(
            year=year,
            slice_type=slice_type,
            month_of_year=month_of_year,
        )

        out.append(
            ObservedPoint(
                date=anchor,
                temperature=_mean([p.temperature for p in bucket]),
            )
        )

    return out


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
        return _aggregate_monthly_observed(
            points,
            date_start=date_start,
            date_end=date_end,
        )

    # year
    return _aggregate_yearly_observed(
        points,
        date_start=date_start,
        date_end=date_end,
        slice_type=slice_type,
        month_of_year=month_of_year,
    )


def _aggregate_monthly_station(
    points: list[DailyDeviationPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
) -> list[AggregatedDeviationPoint]:
    out: list[AggregatedDeviationPoint] = []

    for month_start in iter_month_starts_intersecting(date_start, date_end):
        year = month_start.year
        month = month_start.month

        bucket = [p for p in points if p.date.year == year and p.date.month == month]
        if not bucket:
            continue

        out.append(
            AggregatedDeviationPoint(
                date=dt.date(year, month, 1),
                temperature=_mean([p.temperature for p in bucket]),
                baseline_mean=_mean([p.baseline_mean for p in bucket]),
            )
        )

    return out


def _aggregate_yearly_station(
    points: list[DailyDeviationPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    slice_type: str,
    month_of_year: int | None = None,
) -> list[AggregatedDeviationPoint]:
    out: list[AggregatedDeviationPoint] = []

    for year_start in iter_year_starts_intersecting(date_start, date_end):
        year = year_start.year
        bucket = [p for p in points if p.date.year == year]
        if not bucket:
            continue

        anchor = _year_anchor_date(
            year=year,
            slice_type=slice_type,
            month_of_year=month_of_year,
        )

        out.append(
            AggregatedDeviationPoint(
                date=anchor,
                temperature=_mean([p.temperature for p in bucket]),
                baseline_mean=_mean([p.baseline_mean for p in bucket]),
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
        return _aggregate_monthly_station(
            points,
            date_start=date_start,
            date_end=date_end,
        )

    # year
    return _aggregate_yearly_station(
        points,
        date_start=date_start,
        date_end=date_end,
        slice_type=slice_type,
        month_of_year=month_of_year,
    )
