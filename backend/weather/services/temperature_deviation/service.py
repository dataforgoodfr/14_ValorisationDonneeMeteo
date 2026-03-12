from __future__ import annotations

import datetime as dt
from collections import defaultdict

from weather.utils.date_range import period_start

from .protocols import TemperatureDeviationDailyDataSource
from .types import (
    AggregatedDeviationPoint,
    DailyDeviationPoint,
    DailyDeviationSeriesQuery,
)


def _aggregate(
    daily: list[DailyDeviationPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
) -> list[AggregatedDeviationPoint]:
    daily = [p for p in daily if date_start <= p.date <= date_end]

    if granularity == "day":
        return [
            AggregatedDeviationPoint(
                date=p.date,
                temperature=p.temperature,
                baseline_mean=p.baseline_mean,
            )
            for p in sorted(daily, key=lambda x: x.date)
        ]

    buckets: dict[dt.date, list[DailyDeviationPoint]] = defaultdict(list)
    for p in daily:
        buckets[period_start(p.date, granularity)].append(p)

    out: list[AggregatedDeviationPoint] = []
    for start_date in sorted(buckets.keys()):
        pts = buckets[start_date]
        out.append(
            AggregatedDeviationPoint(
                date=start_date,
                temperature=sum(x.temperature for x in pts) / len(pts),
                baseline_mean=sum(x.baseline_mean for x in pts) / len(pts),
            )
        )
    return out


def _point_to_payload(p: AggregatedDeviationPoint) -> dict:
    return {
        "date": p.date,
        "temperature": round(p.temperature, 2),
        "baseline_mean": round(p.baseline_mean, 2),
        "deviation": round(p.deviation, 2),
    }


def compute_temperature_deviation(
    *,
    data_source: TemperatureDeviationDailyDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    station_ids: tuple[str, ...] = (),
    include_national: bool = True,
) -> dict:
    query = DailyDeviationSeriesQuery(
        date_start=date_start,
        date_end=date_end,
        station_ids=station_ids,
        include_national=include_national,
    )

    series: list[dict] = []

    if include_national:
        national_daily = data_source.fetch_national_daily_series(query)
        nat_points = _aggregate(
            national_daily,
            date_start=date_start,
            date_end=date_end,
            granularity=granularity,
        )
        series.append(
            {
                "is_national": True,
                "data": [_point_to_payload(p) for p in nat_points],
            }
        )

    station_daily_series = data_source.fetch_station_daily_series(query)
    for station_series in station_daily_series:
        pts = _aggregate(
            station_series.points,
            date_start=date_start,
            date_end=date_end,
            granularity=granularity,
        )
        series.append(
            {
                "is_national": False,
                "station_id": station_series.station_id,
                "station_name": station_series.station_name,
                "data": [_point_to_payload(p) for p in pts],
            }
        )

    return {"series": series}
