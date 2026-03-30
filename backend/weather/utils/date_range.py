from __future__ import annotations

import calendar
import datetime as dt
from collections.abc import Iterator


def clamp_day_to_month_end(year: int, month: int, day: int) -> int:
    return min(day, calendar.monthrange(year, month)[1])


def iter_days_intersecting(date_start: dt.date, date_end: dt.date) -> Iterator[dt.date]:
    """Renvoie tous les jours entre date_start et date_end inclus."""
    cur = date_start
    one_day = dt.timedelta(days=1)
    while cur <= date_end:
        yield cur
        cur += one_day


def iter_month_starts_intersecting(
    date_start: dt.date, date_end: dt.date
) -> Iterator[dt.date]:
    """
    Renvoie les débuts de mois (YYYY-MM-01) qui intersectent l'intervalle [date_start, date_end].
    """
    cur = dt.date(date_start.year, date_start.month, 1)
    last = dt.date(date_end.year, date_end.month, 1)

    while cur <= last:
        yield cur
        if cur.month == 12:
            cur = dt.date(cur.year + 1, 1, 1)
        else:
            cur = dt.date(cur.year, cur.month + 1, 1)


def iter_year_starts_intersecting(
    date_start: dt.date, date_end: dt.date
) -> Iterator[dt.date]:
    """
    Renvoie les débuts d'année (YYYY-01-01) qui intersectent l'intervalle [date_start, date_end].
    """
    for year in range(date_start.year, date_end.year + 1):
        yield dt.date(year, 1, 1)


def days_in_month_in_range(
    *, date_start: dt.date, date_end: dt.date, month: int
) -> tuple[dt.date, ...]:
    return tuple(
        d for d in iter_days_intersecting(date_start, date_end) if d.month == month
    )


def monthly_points_in_range(
    *, date_start: dt.date, date_end: dt.date, day_of_month: int
) -> tuple[dt.date, ...]:
    out: list[dt.date] = []
    for first in iter_month_starts_intersecting(date_start, date_end):
        y, m = first.year, first.month
        target_day = clamp_day_to_month_end(y, m, day_of_month)
        candidate = dt.date(y, m, target_day)
        if date_start <= candidate <= date_end:
            out.append(candidate)
    return tuple(out)


def yearly_points_in_range(
    *, date_start: dt.date, date_end: dt.date, month: int, day_of_month: int
) -> tuple[dt.date, ...]:
    out: list[dt.date] = []
    for y in range(date_start.year, date_end.year + 1):
        target_day = clamp_day_to_month_end(y, month, day_of_month)
        candidate = dt.date(y, month, target_day)
        if date_start <= candidate <= date_end:
            out.append(candidate)
    return tuple(out)


def period_start(d: dt.date, granularity: str) -> dt.date:
    if granularity == "day":
        return d
    if granularity == "month":
        return dt.date(d.year, d.month, 1)
    if granularity == "year":
        return dt.date(d.year, 1, 1)
    raise ValueError(f"Unknown granularity: {granularity}")
