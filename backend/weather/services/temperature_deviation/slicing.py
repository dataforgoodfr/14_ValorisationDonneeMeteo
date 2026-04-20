from collections import defaultdict

from weather.utils.date_range import clamp_day_to_month_end

from .types import DailyDeviationPoint, ObservedPoint


def _select_monthly_observed_points(
    daily: list[ObservedPoint],
    *,
    day_of_month: int,
) -> list[ObservedPoint]:
    by_month: dict[tuple[int, int], list[ObservedPoint]] = defaultdict(list)
    for point in daily:
        by_month[(point.date.year, point.date.month)].append(point)

    selected: list[ObservedPoint] = []
    for (year, month), points in sorted(by_month.items()):
        target_day = clamp_day_to_month_end(year, month, day_of_month)
        chosen = next((point for point in points if point.date.day == target_day), None)
        if chosen is None:
            continue
        selected.append(chosen)

    return selected


def _select_yearly_observed_points(
    daily: list[ObservedPoint],
    *,
    month_of_year: int,
    day_of_month: int,
) -> list[ObservedPoint]:
    by_year: dict[int, list[ObservedPoint]] = defaultdict(list)
    for point in daily:
        by_year[point.date.year].append(point)

    selected: list[ObservedPoint] = []
    for year, points in sorted(by_year.items()):
        target_day = clamp_day_to_month_end(year, month_of_year, day_of_month)
        chosen = next(
            (
                point
                for point in points
                if point.date.month == month_of_year and point.date.day == target_day
            ),
            None,
        )
        if chosen is None:
            continue
        selected.append(chosen)

    return selected


def _select_monthly_station_points(
    daily: list[DailyDeviationPoint],
    *,
    day_of_month: int,
) -> list[DailyDeviationPoint]:
    by_month: dict[tuple[int, int], list[DailyDeviationPoint]] = defaultdict(list)
    for point in daily:
        by_month[(point.date.year, point.date.month)].append(point)

    selected: list[DailyDeviationPoint] = []
    for (year, month), points in sorted(by_month.items()):
        target_day = clamp_day_to_month_end(year, month, day_of_month)
        chosen = next((point for point in points if point.date.day == target_day), None)
        if chosen is None:
            continue
        selected.append(chosen)

    return selected


def _select_yearly_station_points(
    daily: list[DailyDeviationPoint],
    *,
    month_of_year: int,
    day_of_month: int,
) -> list[DailyDeviationPoint]:
    by_year: dict[int, list[DailyDeviationPoint]] = defaultdict(list)
    for point in daily:
        by_year[point.date.year].append(point)

    selected: list[DailyDeviationPoint] = []
    for year, points in sorted(by_year.items()):
        target_day = clamp_day_to_month_end(year, month_of_year, day_of_month)
        chosen = next(
            (
                point
                for point in points
                if point.date.month == month_of_year and point.date.day == target_day
            ),
            None,
        )
        if chosen is None:
            continue
        selected.append(chosen)

    return selected


def apply_slice_to_observed(
    daily: list[ObservedPoint],
    *,
    granularity: str,
    slice_type: str,
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> list[ObservedPoint]:
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
        return _select_monthly_observed_points(
            daily,
            day_of_month=day_of_month,
        )

    if granularity == "year":
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")

        return _select_yearly_observed_points(
            daily,
            month_of_year=month_of_year,
            day_of_month=day_of_month,
        )

    raise ValueError(
        f"Combinaison invalide granularity={granularity}, slice_type={slice_type}"
    )


def apply_slice_to_station_daily(
    daily: list[DailyDeviationPoint],
    *,
    granularity: str,
    slice_type: str,
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> list[DailyDeviationPoint]:
    """
    Identique à apply_slice_to_observed mais sur DailyDeviationPoint.
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
        return _select_monthly_station_points(
            daily,
            day_of_month=day_of_month,
        )

    if granularity == "year":
        if month_of_year is None:
            raise ValueError("month_of_year ne doit pas être None")

        return _select_yearly_station_points(
            daily,
            month_of_year=month_of_year,
            day_of_month=day_of_month,
        )

    raise ValueError(
        f"Combinaison invalide granularity={granularity}, slice_type={slice_type}"
    )
