import calendar
import datetime as dt


def clamp_day_to_month_end(year: int, month: int, day: int) -> int:
    """
    Clamp un jour au dernier jour valide du mois.
    Exemple : 30 février 2024 -> 29
    """
    last_day = calendar.monthrange(year, month)[1]
    return min(day, last_day)


def _next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def yearly_points_in_range(
    *,
    date_start: dt.date,
    date_end: dt.date,
    month: int,
    day_of_month: int,
) -> tuple[dt.date, ...]:
    out: list[dt.date] = []
    for y in range(date_start.year, date_end.year + 1):
        target_day = clamp_day_to_month_end(y, month, day_of_month)
        candidate = dt.date(y, month, target_day)
        if date_start <= candidate <= date_end:
            out.append(candidate)
    return tuple(out)


def monthly_points_in_range(
    *,
    date_start: dt.date,
    date_end: dt.date,
    day_of_month: int,
) -> tuple[dt.date, ...]:
    out: list[dt.date] = []

    y, m = date_start.year, date_start.month

    # On itère mois par mois sur l'intervalle
    while True:
        first = dt.date(y, m, 1)
        if first > date_end:
            break

        target_day = clamp_day_to_month_end(y, m, day_of_month)
        candidate = dt.date(y, m, target_day)

        if date_start <= candidate <= date_end:
            out.append(candidate)

        y, m = _next_month(y, m)

    return tuple(out)


def days_in_month_in_range(
    *,
    date_start: dt.date,
    date_end: dt.date,
    month: int,
) -> tuple[dt.date, ...]:
    out: list[dt.date] = []
    d = date_start
    one_day = dt.timedelta(days=1)
    while d <= date_end:
        if d.month == month:
            out.append(d)
        d += one_day
    return tuple(out)
