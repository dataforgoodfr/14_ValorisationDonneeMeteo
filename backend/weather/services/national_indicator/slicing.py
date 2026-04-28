from collections import defaultdict

from weather.services.national_indicator.types import ObservedPoint
from weather.utils.date_range import clamp_day_to_month_end


def apply_slice(
    daily: list[ObservedPoint],
    *,
    granularity: str,
    slice_type: str,
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> list[ObservedPoint]:
    """
    Applique la logique "slice" sur la série journalière observée.

    slice_type:
    - "full" : on conserve tous les jours de la fenêtre
    - "month_of_year" : on conserve uniquement les jours du mois (toutes années)
      (pertinent surtout quand granularity="year")
    - "day_of_month" :
        - granularity="month" : on sélectionne 1 jour par mois (clamp)
        - granularity="year" : on sélectionne 1 jour par année (month_of_year + clamp)
        - granularity="day" : interdit
    """
    if slice_type == "full":
        return daily

    if slice_type == "month_of_year":
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")
        return [p for p in daily if p.date.month == month_of_year]

    if slice_type != "day_of_month":
        raise ValueError(f"slice_type non supporté: {slice_type}")

    if day_of_month is None:
        raise ValueError("day_of_month ne doit pas être None")

    if granularity == "month":
        by_month: dict[tuple[int, int], list[ObservedPoint]] = defaultdict(list)
        for p in daily:
            by_month[(p.date.year, p.date.month)].append(p)

        selected: list[ObservedPoint] = []
        for (y, m), pts in sorted(by_month.items()):
            target_day = clamp_day_to_month_end(y, m, day_of_month)
            chosen = next((pp for pp in pts if pp.date.day == target_day), None)
            if chosen is None:
                raise ValueError(
                    f"Jour {target_day} introuvable dans les données pour {y}-{m:02d}"
                )
            selected.append(chosen)

        return selected

    if granularity == "year":
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")

        by_year: dict[int, list[ObservedPoint]] = defaultdict(list)
        for p in daily:
            by_year[p.date.year].append(p)

        selected: list[ObservedPoint] = []
        for y, pts in sorted(by_year.items()):
            target_day = clamp_day_to_month_end(y, month_of_year, day_of_month)
            chosen = next(
                (
                    pp
                    for pp in pts
                    if pp.date.month == month_of_year and pp.date.day == target_day
                ),
                None,
            )
            if chosen is None:
                raise ValueError(
                    f"Jour {target_day} introuvable dans les données pour {y}"
                )
            selected.append(chosen)

        return selected

    raise ValueError(
        f"Combinaison invalide granularity={granularity}, slice_type={slice_type}"
    )
