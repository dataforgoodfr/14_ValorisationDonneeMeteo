import datetime as dt

from weather.services.national_indicator.types import DailyPoint, OutputPoint
from weather.services.time_windows import (
    iter_month_starts_intersecting,
    iter_year_starts_intersecting,
)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _to_output_point(p: DailyPoint, anchor: dt.date | None = None) -> OutputPoint:
    """
    Convertit un DailyPoint en OutputPoint.
    Si anchor est fourni, on l'utilise comme date de sortie, sinon on garde p.date.
    """
    d = anchor if anchor is not None else p.date
    return OutputPoint(
        date=d,
        temperature=p.temperature,
        baseline_mean=p.baseline_mean,
        baseline_std_dev_upper=p.baseline_std_dev_upper,
        baseline_std_dev_lower=p.baseline_std_dev_lower,
        baseline_max=p.baseline_max,
        baseline_min=p.baseline_min,
    )


def _aggregate_bucket(anchor: dt.date, pts: list[DailyPoint]) -> OutputPoint:
    """
    Agrège un bucket (mois ou année) en un point.

    Choix de calcul :
    - moyenne sur temperature, baseline_mean et bandes sigma
    - enveloppe sur baseline_min/baseline_max (min/max sur la période)
      (plus crédible qu'une moyenne pour une enveloppe)
    """
    return OutputPoint(
        date=anchor,
        temperature=_mean([p.temperature for p in pts]),
        baseline_mean=_mean([p.baseline_mean for p in pts]),
        baseline_std_dev_upper=_mean([p.baseline_std_dev_upper for p in pts]),
        baseline_std_dev_lower=_mean([p.baseline_std_dev_lower for p in pts]),
        baseline_max=max(p.baseline_max for p in pts),
        baseline_min=min(p.baseline_min for p in pts),
    )


def aggregate(
    daily_sliced: list[DailyPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str,
    month_of_year: int | None = None,
) -> list[OutputPoint]:
    """
    Agrège après slice.

    On itère explicitement sur les buckets "intersectants" (mois / années)
    via iter_month_starts_intersecting / iter_year_starts_intersecting, afin
    de coller à la sémantique "un bucket par période intersectant l'intervalle".

    - granularity="day" : identité (un point par jour)
    - granularity="month" :
        - slice_type="day_of_month" : déjà 1 point par mois (date précise) -> identité
        - sinon : moyenne par mois, date ancrée au 1er du mois (YYYY-MM-01)
    - granularity="year" :
        - slice_type="day_of_month" : déjà 1 point par année (date précise) -> identité
        - slice_type="month_of_year" : on agrège par année (moyenne du mois sélectionné),
          et la date de sortie est ancrée sur YYYY-MM-01 (M = month_of_year)
        - slice_type="full" : agrège par année, ancre sur YYYY-01-01
    """
    if granularity == "day":
        return [_to_output_point(p) for p in daily_sliced]

    if granularity == "month" and slice_type == "day_of_month":
        # Déjà 1 point par mois (un jour précis), donc pas de moyenne
        return [_to_output_point(p) for p in daily_sliced]

    if granularity == "year" and slice_type == "day_of_month":
        # Déjà 1 point par année (un jour précis), donc pas de moyenne
        return [_to_output_point(p) for p in daily_sliced]

    if granularity == "month":
        out: list[OutputPoint] = []
        for month_start in iter_month_starts_intersecting(date_start, date_end):
            y, m = month_start.year, month_start.month
            pts = [p for p in daily_sliced if p.date.year == y and p.date.month == m]
            if not pts:
                # Peut arriver si un slice filtre tous les jours du mois
                continue
            anchor = dt.date(y, m, 1)
            out.append(_aggregate_bucket(anchor, pts))
        return out

    # granularity == "year"
    out: list[OutputPoint] = []
    for year_start in iter_year_starts_intersecting(date_start, date_end):
        y = year_start.year
        pts = [p for p in daily_sliced if p.date.year == y]
        if not pts:
            continue

        if slice_type == "month_of_year":
            if month_of_year is None:
                raise ValueError("month_of_year ne doit pas être None")
            anchor = dt.date(y, month_of_year, 1)
        else:
            anchor = dt.date(y, 1, 1)

        out.append(_aggregate_bucket(anchor, pts))
    return out
