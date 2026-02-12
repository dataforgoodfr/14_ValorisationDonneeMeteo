import datetime as dt

from weather.services.time_windows import iter_year_starts_intersecting
from weather.utils.dates import clamp_day_to_month_end


def compute_source_window(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str,
    month_of_year: int | None,
) -> tuple[dt.date, dt.date]:
    """
    Détermine la fenêtre réelle utilisée pour générer la série journalière.

    Cas particulier :
    - granularity="year" avec slice_type="month_of_year" ou "day_of_month"
      -> on veut un point par année intersectante, même si le mois ciblé
         est hors [date_start, date_end].
      -> on couvre donc le mois ciblé sur toutes les années intersectantes.
    """
    if granularity == "year" and slice_type in ("month_of_year", "day_of_month"):
        assert month_of_year is not None

        years = [d.year for d in iter_year_starts_intersecting(date_start, date_end)]
        # dates validées en amont => au moins une année
        start = dt.date(years[0], month_of_year, 1)
        last_day = clamp_day_to_month_end(years[-1], month_of_year, 31)
        end = dt.date(years[-1], month_of_year, last_day)

        return start, end

    return date_start, date_end
