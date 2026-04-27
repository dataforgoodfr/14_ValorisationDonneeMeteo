import datetime as dt

from weather.utils.date_range import (
    clamp_day_to_month_end,
    iter_year_starts_intersecting,
)


def _full_month_source_window(
    *,
    date_start: dt.date,
    date_end: dt.date,
) -> tuple[dt.date, dt.date]:
    start = dt.date(date_start.year, date_start.month, 1)
    last_day = clamp_day_to_month_end(date_end.year, date_end.month, 31)
    end = dt.date(date_end.year, date_end.month, last_day)
    return start, end


def _full_year_source_window(
    *,
    date_start: dt.date,
    date_end: dt.date,
) -> tuple[dt.date, dt.date]:
    start = dt.date(date_start.year, 1, 1)
    end = dt.date(date_end.year, 12, 31)
    return start, end


def _year_slice_source_window(
    *,
    date_start: dt.date,
    date_end: dt.date,
    month_of_year: int,
) -> tuple[dt.date, dt.date]:
    years = [d.year for d in iter_year_starts_intersecting(date_start, date_end)]

    start = dt.date(years[0], month_of_year, 1)
    last_day = clamp_day_to_month_end(years[-1], month_of_year, 31)
    end = dt.date(years[-1], month_of_year, last_day)

    return start, end


def compute_source_window(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str,
    month_of_year: int | None,
) -> tuple[dt.date, dt.date]:
    # --- CAS HISTORIQUE deviation ---

    # Mois → élargir au mois complet
    if granularity == "month" and slice_type == "full":
        return _full_month_source_window(
            date_start=date_start,
            date_end=date_end,
        )

    # Année → élargir à l'année complète
    if granularity == "year" and slice_type == "full":
        return _full_year_source_window(
            date_start=date_start,
            date_end=date_end,
        )

    # --- CAS SLICING (nouveau) ---

    if granularity == "year" and slice_type in ("month_of_year", "day_of_month"):
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")

        return _year_slice_source_window(
            date_start=date_start,
            date_end=date_end,
            month_of_year=month_of_year,
        )

    # --- fallback ---
    return date_start, date_end
