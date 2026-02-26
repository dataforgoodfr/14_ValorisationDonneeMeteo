from __future__ import annotations

import datetime as dt

from weather.utils.dates import clamp_day_to_month_end

from .aggregation import aggregate
from .protocols import NationalIndicatorDailyDataSource
from .slicing import apply_slice
from .source_window import compute_source_window
from .types import DailySeriesQuery


def compute_target_dates(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str,
    month_of_year: int | None,
    day_of_month: int | None,
) -> tuple[dt.date, ...] | None:
    """
    Retourne une liste de dates exactes à prélever pour réduire la volumétrie DB.
    Si None, il faut prélever la fenêtre complète [date_start, date_end].

    IMPORTANT: on reproduit la sémantique de apply_slice() (clamp compris).
    """

    if slice_type == "full":
        return None

    if slice_type == "month_of_year":
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")

        # On veut tous les jours du mois X entre date_start et date_end
        # => on construit la liste exacte des dates à garder.
        out: list[dt.date] = []
        d = date_start
        one_day = dt.timedelta(days=1)
        while d <= date_end:
            if d.month == month_of_year:
                out.append(d)
            d += one_day
        return tuple(out)

    # slice_type == "day_of_month"
    if day_of_month is None:
        raise ValueError("day_of_month ne doit pas être None")

    if granularity == "month":
        # 1 point par mois: (année, mois) -> clamp(day_of_month) -> date
        out: list[dt.date] = []
        y, m = date_start.year, date_start.month

        def next_month(year: int, month: int) -> tuple[int, int]:
            if month == 12:
                return year + 1, 1
            return year, month + 1

        # On itère mois par mois sur l'intervalle
        while True:
            first = dt.date(y, m, 1)
            if first > date_end:
                break

            target_day = clamp_day_to_month_end(y, m, day_of_month)
            candidate = dt.date(y, m, target_day)

            if date_start <= candidate <= date_end:
                out.append(candidate)

            y, m = next_month(y, m)

        return tuple(out)

    if granularity == "year":
        # 1 point par année: mois fixé (month_of_year) + clamp(day_of_month)
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")

        out: list[dt.date] = []
        for y in range(date_start.year, date_end.year + 1):
            target_day = clamp_day_to_month_end(y, month_of_year, day_of_month)
            candidate = dt.date(y, month_of_year, target_day)
            if date_start <= candidate <= date_end:
                out.append(candidate)
        return tuple(out)

    # Si granularity == "day", le serializer doit empêcher day_of_month
    return None


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
    target_dates = compute_target_dates(
        date_start=src_start,
        date_end=src_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )

    query = DailySeriesQuery(
        date_start=src_start,
        date_end=src_end,
        target_dates=target_dates,
    )

    daily = data_source.fetch_daily_series(query)

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
