import calendar
import datetime as dt


def _clamp_day(year: int, month: int, day: int) -> int:
    """Clamp-to-last-day systématique."""
    last = calendar.monthrange(year, month)[1]
    return min(day, last)


def _iter_years(date_start: dt.date, date_end: dt.date):
    """
    Renvoie les débuts d'années (YYYY-01-01) pour toutes les années
    qui intersectent l'intervalle [date_start, date_end].
    """
    start = dt.date(date_start.year, 1, 1)
    end = dt.date(date_end.year, 1, 1)
    for y in range(start.year, end.year + 1):
        yield dt.date(y, 1, 1)


def _iter_months(date_start: dt.date, date_end: dt.date):
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


def _iter_days(date_start: dt.date, date_end: dt.date):
    cur = date_start
    while cur <= date_end:
        yield cur
        cur = cur + dt.timedelta(days=1)


def generate_fake_national_indicator(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str = "full",
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> dict:
    """
    ⚠MOCK IMPLEMENTATION (sans BDD)
    Conforme au contrat OpenAPI (metadata + time_series).
    """

    baseline = "1991-2020"

    # Baseline "pipot" mais stable
    baseline_mean = 12.8
    std = 0.8
    baseline_min = baseline_mean - 2.0
    baseline_max = baseline_mean + 2.0

    # Détermine les dates de la série (axe X)
    if granularity == "year":
        axis_dates = list(_iter_years(date_start, date_end))
    elif granularity == "month":
        axis_dates = list(_iter_months(date_start, date_end))
    else:  # day
        axis_dates = list(_iter_days(date_start, date_end))

    # Construit metadata (sans champs inutiles)
    metadata = {
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
        "baseline": baseline,
        "granularity": granularity,
        "slice_type": slice_type,
    }
    if month_of_year is not None:
        metadata["month_of_year"] = month_of_year
    if day_of_month is not None:
        metadata["day_of_month"] = day_of_month

    # Calcul "pipot" : une température par point de l’axe
    # Le slice influence seulement la DATE retournée (pas le calcul) => suffisant pour mock.
    time_series = []
    for i, axis_d in enumerate(axis_dates):
        # Date du point = date d’ancrage de la période
        # - year => YYYY-01-01
        # - month => YYYY-MM-01
        # - day => YYYY-MM-DD
        point_date = axis_d

        # Si on est en mode "échantillon jour" (day_of_month), on positionne un jour
        if slice_type == "day_of_month":
            if granularity == "month":
                # N-ième jour de chaque mois (clamp)
                dd = _clamp_day(axis_d.year, axis_d.month, int(day_of_month))
                point_date = dt.date(axis_d.year, axis_d.month, dd)
            elif granularity == "year":
                # Jour précis de l'année => month_of_year requis (validé par serializer)
                mm = int(month_of_year)
                dd = _clamp_day(axis_d.year, mm, int(day_of_month))
                point_date = dt.date(axis_d.year, mm, dd)
            else:
                # granularity=day => slice_type doit être full (normalement jamais ici)
                point_date = axis_d

        elif slice_type == "month_of_year":
            # agrégat sur un mois donné (granularity=year)
            # On représente ça par une date ancrée au 1er jour du mois ciblé de l'année
            if granularity == "year":
                point_date = dt.date(axis_d.year, int(month_of_year), 1)

        # Température mock : variation déterministe
        temp = baseline_mean + ((i % 6) - 2) * 0.3  # -0.6..+0.9

        time_series.append(
            {
                "date": point_date.isoformat(),
                "temperature": float(round(temp, 1)),
                "baseline_mean": float(baseline_mean),
                "baseline_std_dev_upper": float(round(baseline_mean + std, 1)),
                "baseline_std_dev_lower": float(round(baseline_mean - std, 1)),
                "baseline_max": float(round(baseline_max, 1)),
                "baseline_min": float(round(baseline_min, 1)),
            }
        )

    return {
        "metadata": metadata,
        "time_series": time_series,
    }
