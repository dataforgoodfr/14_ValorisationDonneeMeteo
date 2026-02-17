import datetime as dt
from collections.abc import Iterator


def iter_year_starts_intersecting(
    date_start: dt.date, date_end: dt.date
) -> Iterator[dt.date]:
    """
    Renvoie les débuts d'années (YYYY-01-01) pour toutes les années
    qui intersectent l'intervalle [date_start, date_end].
    """
    for year in range(date_start.year, date_end.year + 1):
        yield dt.date(year, 1, 1)


def iter_month_starts_intersecting(
    date_start: dt.date, date_end: dt.date
) -> Iterator[dt.date]:
    """
    Renvoie les débuts de mois (YYYY-MM-01) pour tous les mois
    qui intersectent l'intervalle [date_start, date_end].
    """
    cur = dt.date(date_start.year, date_start.month, 1)
    end = dt.date(date_end.year, date_end.month, 1)

    while cur <= end:
        yield cur
        if cur.month == 12:
            cur = dt.date(cur.year + 1, 1, 1)
        else:
            cur = dt.date(cur.year, cur.month + 1, 1)


def iter_days_intersecting(date_start: dt.date, date_end: dt.date) -> Iterator[dt.date]:
    """
    Renvoie tous les jours entre date_start et date_end inclus.
    """
    cur = date_start
    while cur <= date_end:
        yield cur
        cur += dt.timedelta(days=1)
