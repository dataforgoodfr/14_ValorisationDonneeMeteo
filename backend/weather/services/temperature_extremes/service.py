from __future__ import annotations

from collections import defaultdict

from weather.utils.date_range import (
    iter_days_intersecting,
    iter_month_starts_intersecting,
    iter_year_starts_intersecting,
    period_start,
)

from .protocols import ExtremesGraphDataSource, ExtremesOverviewDataSource
from .types import (
    DailyExtremesPoint,
    ExtremesGraphPoint,
    ExtremesGraphQuery,
    ExtremesGraphResult,
    ExtremesOverviewQuery,
    NationalExtremesSeries,
    StationExtremesSeries,
)


def _bucket_starts(query: ExtremesGraphQuery) -> set:
    if query.granularity == "day":
        return set(iter_days_intersecting(query.date_start, query.date_end))
    if query.granularity == "month":
        return set(iter_month_starts_intersecting(query.date_start, query.date_end))
    if query.granularity == "year":
        return set(iter_year_starts_intersecting(query.date_start, query.date_end))
    raise ValueError(f"Granularité non supportée : {query.granularity}")


def _bucket_points_by_period(
    points: list[DailyExtremesPoint], granularity: str
) -> dict:
    buckets: dict = defaultdict(lambda: {"tn": [], "tx": []})
    for p in points:
        if p.tn is None and p.tx is None:
            continue
        start = period_start(p.date, granularity)
        if p.tn is not None:
            buckets[start]["tn"].append(p.tn)
        if p.tx is not None:
            buckets[start]["tx"].append(p.tx)
    return buckets


def _average_buckets(buckets: dict, valid_starts: set) -> list[ExtremesGraphPoint]:
    result = []
    for start_date in sorted(buckets.keys()):
        if start_date not in valid_starts:
            continue
        tn_vals = buckets[start_date]["tn"]
        tx_vals = buckets[start_date]["tx"]
        if not tn_vals or not tx_vals:
            continue
        result.append(
            ExtremesGraphPoint(
                date=start_date,
                tnm=round(sum(tn_vals) / len(tn_vals), 2),
                txm=round(sum(tx_vals) / len(tx_vals), 2),
            )
        )
    return result


def _aggregate(
    points: list[DailyExtremesPoint],
    query: ExtremesGraphQuery,
) -> list[ExtremesGraphPoint]:
    buckets = _bucket_points_by_period(points, query.granularity)
    return _average_buckets(buckets, _bucket_starts(query))


def compute_extremes_graph(
    *,
    data_source: ExtremesGraphDataSource,
    query: ExtremesGraphQuery,
) -> dict:
    national = None
    stations = []

    if query.has_station_filter:
        station_series = data_source.fetch_daily_series(query)
        stations = [
            StationExtremesSeries(
                station_id=s.station_id,
                station_name=s.station_name,
                data=_aggregate(s.points, query),
            )
            for s in station_series
        ]
    elif query.has_territory_filter:
        station_series = data_source.fetch_daily_series(query)
        all_points = [p for s in station_series for p in s.points]
        national = NationalExtremesSeries(data=_aggregate(all_points, query))
    else:
        national_points = data_source.fetch_national_daily_series(query)
        national = NationalExtremesSeries(data=_aggregate(national_points, query))

    result = ExtremesGraphResult(national=national, stations=stations)

    payload: dict = {
        "stations": [
            {
                "station_id": s.station_id,
                "station_name": s.station_name,
                "data": [{"date": p.date, "tnm": p.tnm, "txm": p.txm} for p in s.data],
            }
            for s in result.stations
        ]
    }

    if result.national is not None:
        payload["national"] = {
            "data": [
                {"date": p.date, "tnm": p.tnm, "txm": p.txm}
                for p in result.national.data
            ]
        }

    return payload


def compute_extremes_overview(
    *,
    data_source: ExtremesOverviewDataSource,
    query: ExtremesOverviewQuery,
) -> dict:
    result = data_source.fetch_station_overview(query)

    return {
        "pagination": {
            "total_count": result.pagination.total_count,
            "limit": result.pagination.limit,
            "offset": result.pagination.offset,
        },
        "stations": [
            {
                "station_id": s.station_id,
                "station_name": s.station_name,
                "txm": round(s.txm, 2),
                "tnm": round(s.tnm, 2),
                "tmm": round(s.tmm, 2),
                "lat": s.lat,
                "lon": s.lon,
                "alt": s.alt,
                "department": s.department,
                "region": s.region,
                "classe_recente": s.classe_recente,
                "date_de_creation": s.date_de_creation,
                "date_de_fermeture": s.date_de_fermeture,
            }
            for s in result.stations
        ],
    }
