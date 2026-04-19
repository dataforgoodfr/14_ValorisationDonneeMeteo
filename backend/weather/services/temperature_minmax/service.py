from __future__ import annotations

from collections import defaultdict

from weather.utils.date_range import (
    iter_days_intersecting,
    iter_month_starts_intersecting,
    iter_year_starts_intersecting,
    period_start,
)

from .protocols import MinMaxGraphDataSource
from .types import (
    DailyMinMaxPoint,
    MinMaxGraphPoint,
    MinMaxGraphQuery,
    MinMaxGraphResult,
    NationalMinMaxSeries,
    StationMinMaxSeries,
)


def _bucket_starts(query: MinMaxGraphQuery) -> set:
    if query.granularity == "day":
        return set(iter_days_intersecting(query.date_start, query.date_end))
    if query.granularity == "month":
        return set(iter_month_starts_intersecting(query.date_start, query.date_end))
    if query.granularity == "year":
        return set(iter_year_starts_intersecting(query.date_start, query.date_end))
    raise ValueError(f"Granularité non supportée : {query.granularity}")


def _aggregate(
    points: list[DailyMinMaxPoint],
    query: MinMaxGraphQuery,
) -> list[MinMaxGraphPoint]:
    buckets: dict = defaultdict(lambda: {"tmin": [], "tmax": []})

    for p in points:
        if p.tmin is None and p.tmax is None:
            continue
        start = period_start(p.date, query.granularity)
        if p.tmin is not None:
            buckets[start]["tmin"].append(p.tmin)
        if p.tmax is not None:
            buckets[start]["tmax"].append(p.tmax)

    valid_starts = _bucket_starts(query)

    result = []
    for start_date in sorted(buckets.keys()):
        if start_date not in valid_starts:
            continue
        tmin_vals = buckets[start_date]["tmin"]
        tmax_vals = buckets[start_date]["tmax"]
        if not tmin_vals or not tmax_vals:
            continue
        result.append(
            MinMaxGraphPoint(
                date=start_date,
                tmin_mean=round(sum(tmin_vals) / len(tmin_vals), 2),
                tmax_mean=round(sum(tmax_vals) / len(tmax_vals), 2),
            )
        )
    return result


def compute_minmax_graph(
    *,
    data_source: MinMaxGraphDataSource,
    query: MinMaxGraphQuery,
) -> dict:
    national = None
    stations = []

    if query.has_station_filter:
        station_series = data_source.fetch_daily_series(query)
        stations = [
            StationMinMaxSeries(
                station_id=s.station_id,
                station_name=s.station_name,
                data=_aggregate(s.points, query),
            )
            for s in station_series
        ]
    elif query.has_territory_filter:
        station_series = data_source.fetch_daily_series(query)
        all_points = [p for s in station_series for p in s.points]
        national = NationalMinMaxSeries(data=_aggregate(all_points, query))
    else:
        national_points = data_source.fetch_national_daily_series(query)
        national = NationalMinMaxSeries(data=_aggregate(national_points, query))

    result = MinMaxGraphResult(national=national, stations=stations)

    payload: dict = {
        "stations": [
            {
                "station_id": s.station_id,
                "station_name": s.station_name,
                "data": [
                    {"date": p.date, "tmin_mean": p.tmin_mean, "tmax_mean": p.tmax_mean}
                    for p in s.data
                ],
            }
            for s in result.stations
        ]
    }

    if result.national is not None:
        payload["national"] = {
            "data": [
                {"date": p.date, "tmin_mean": p.tmin_mean, "tmax_mean": p.tmax_mean}
                for p in result.national.data
            ]
        }

    return payload
