from __future__ import annotations

import datetime as dt
from collections import defaultdict

from weather.utils.date_range import (
    iter_days_intersecting,
    iter_month_starts_intersecting,
    iter_year_starts_intersecting,
    period_start,
)

from .protocols import TemperatureDeviationDailyDataSource
from .types import (
    AggregatedDeviationPoint,
    DailyDeviationPoint,
    DailyDeviationSeriesQuery,
    NationalDeviationSeries,
    ObservedPoint,
    StationDeviationSeries,
    TemperatureDeviationResult,
)


def _month_end(first_day_of_month: dt.date) -> dt.date:
    if first_day_of_month.month == 12:
        next_month = dt.date(first_day_of_month.year + 1, 1, 1)
    else:
        next_month = dt.date(first_day_of_month.year, first_day_of_month.month + 1, 1)
    return next_month - dt.timedelta(days=1)


def _year_end(first_day_of_year: dt.date) -> dt.date:
    return dt.date(first_day_of_year.year, 12, 31)


def _month_source_window(
    date_start: dt.date, date_end: dt.date
) -> tuple[dt.date, dt.date]:
    month_starts = list(iter_month_starts_intersecting(date_start, date_end))
    start = month_starts[0]
    end = _month_end(month_starts[-1])
    return start, end


def _year_source_window(
    date_start: dt.date, date_end: dt.date
) -> tuple[dt.date, dt.date]:
    year_starts = list(iter_year_starts_intersecting(date_start, date_end))
    start = year_starts[0]
    end = dt.date(year_starts[-1].year, 12, 31)
    return start, end


def _compute_source_window(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
) -> tuple[dt.date, dt.date]:
    if granularity == "day":
        return date_start, date_end

    if granularity == "month":
        return _month_source_window(date_start, date_end)

    if granularity == "year":
        return _year_source_window(date_start, date_end)

    raise ValueError(f"Granularité non supportée : {granularity}")


def _requested_bucket_starts(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
) -> set[dt.date]:
    if granularity == "day":
        return set(iter_days_intersecting(date_start, date_end))

    if granularity == "month":
        return set(iter_month_starts_intersecting(date_start, date_end))

    if granularity == "year":
        return set(iter_year_starts_intersecting(date_start, date_end))

    raise ValueError(f"Granularité non supportée : {granularity}")


def _bucket_days(bucket_start: dt.date, granularity: str) -> tuple[dt.date, ...]:
    if granularity == "day":
        return (bucket_start,)

    if granularity == "month":
        return tuple(iter_days_intersecting(bucket_start, _month_end(bucket_start)))

    if granularity == "year":
        return tuple(iter_days_intersecting(bucket_start, _year_end(bucket_start)))

    raise ValueError(f"Granularité non supportée : {granularity}")


def _aggregate(
    daily: list[DailyDeviationPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
) -> list[AggregatedDeviationPoint]:
    requested_bucket_starts = _requested_bucket_starts(
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
    )

    if granularity == "day":
        return [
            AggregatedDeviationPoint(
                date=p.date,
                temperature=p.temperature,
                baseline_mean=p.baseline_mean,
            )
            for p in sorted(daily, key=lambda x: x.date)
            if p.date in requested_bucket_starts
        ]

    buckets: dict[dt.date, list[DailyDeviationPoint]] = defaultdict(list)
    for p in daily:
        start = period_start(p.date, granularity)
        if start in requested_bucket_starts:
            buckets[start].append(p)

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


def _aggregate_observed(
    observed: list[ObservedPoint],
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
) -> list[ObservedPoint]:
    requested_bucket_starts = _requested_bucket_starts(
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
    )

    if granularity == "day":
        return sorted(
            [p for p in observed if p.date in requested_bucket_starts],
            key=lambda x: x.date,
        )

    buckets: dict[dt.date, list[ObservedPoint]] = defaultdict(list)
    for p in observed:
        start = period_start(p.date, granularity)
        if start in requested_bucket_starts:
            buckets[start].append(p)

    out: list[ObservedPoint] = []
    for start_date in sorted(buckets.keys()):
        pts = buckets[start_date]
        out.append(
            ObservedPoint(
                date=start_date,
                temperature=sum(x.temperature for x in pts) / len(pts),
            )
        )
    return out


def _inject_national_baseline(
    observed_daily: list[ObservedPoint],
    observed_aggregated: list[ObservedPoint],
    *,
    granularity: str,
    data_source: TemperatureDeviationDailyDataSource,
) -> list[AggregatedDeviationPoint]:
    daily_baseline = {
        (p.month, p.day_of_month): p.mean
        for p in data_source.fetch_national_daily_baseline()
    }

    if granularity == "day":
        return [
            AggregatedDeviationPoint(
                date=p.date,
                temperature=p.temperature,
                baseline_mean=daily_baseline[(p.date.month, p.date.day)],
            )
            for p in observed_aggregated
            if (p.date.month, p.date.day) in daily_baseline
        ]

    observed_days_by_bucket: dict[dt.date, set[dt.date]] = defaultdict(set)
    for p in observed_daily:
        observed_days_by_bucket[period_start(p.date, granularity)].add(p.date)

    monthly_baseline = None
    yearly_baseline = None

    if granularity == "month":
        monthly_baseline = {
            p.month: p.mean for p in data_source.fetch_national_monthly_baseline()
        }

    if granularity == "year":
        yearly_baseline = data_source.fetch_national_yearly_baseline()

    out: list[AggregatedDeviationPoint] = []
    for p in observed_aggregated:
        observed_days = observed_days_by_bucket.get(p.date, set())
        if not observed_days:
            continue

        full_bucket_days = set(_bucket_days(p.date, granularity))
        is_complete_bucket = observed_days == full_bucket_days

        if granularity == "month" and is_complete_bucket:
            assert monthly_baseline is not None
            baseline_mean = monthly_baseline[p.date.month]
        elif granularity == "year" and is_complete_bucket:
            if yearly_baseline is None:
                continue
            baseline_mean = yearly_baseline.mean
        else:
            baseline_values = [
                daily_baseline[(d.month, d.day)]
                for d in sorted(observed_days)
                if (d.month, d.day) in daily_baseline
            ]
            if not baseline_values:
                continue
            baseline_mean = sum(baseline_values) / len(baseline_values)

        out.append(
            AggregatedDeviationPoint(
                date=p.date,
                temperature=p.temperature,
                baseline_mean=baseline_mean,
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


def serialize_temperature_deviation_result(
    result: TemperatureDeviationResult,
) -> dict:
    payload = {
        "stations": [
            {
                "station_id": station.station_id,
                "station_name": station.station_name,
                "data": [_point_to_payload(p) for p in station.data],
            }
            for station in result.stations
        ]
    }

    if result.national is not None:
        payload["national"] = {
            "data": [_point_to_payload(p) for p in result.national.data],
        }

    return payload


def compute_temperature_deviation_series(
    *,
    data_source: TemperatureDeviationDailyDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    station_ids: tuple[str, ...] = (),
    include_national: bool = True,
) -> TemperatureDeviationResult:
    src_start, src_end = _compute_source_window(
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
    )

    query = DailyDeviationSeriesQuery(
        date_start=src_start,
        date_end=src_end,
        station_ids=station_ids,
        include_national=include_national,
    )

    national = None
    if include_national:
        national_observed_daily = data_source.fetch_national_observed_series(query)
        national_aggregated_observed = _aggregate_observed(
            national_observed_daily,
            date_start=date_start,
            date_end=date_end,
            granularity=granularity,
        )
        nat_points = _inject_national_baseline(
            national_observed_daily,
            national_aggregated_observed,
            granularity=granularity,
            data_source=data_source,
        )
        national = NationalDeviationSeries(data=nat_points)

    station_daily_series = data_source.fetch_stations_daily_series(query)
    stations = [
        StationDeviationSeries(
            station_id=station_series.station_id,
            station_name=station_series.station_name,
            data=_aggregate(
                station_series.points,
                date_start=date_start,
                date_end=date_end,
                granularity=granularity,
            ),
        )
        for station_series in station_daily_series
    ]

    return TemperatureDeviationResult(
        stations=stations,
        national=national,
    )


def compute_temperature_deviation(
    *,
    data_source: TemperatureDeviationDailyDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    station_ids: tuple[str, ...] = (),
    include_national: bool = True,
) -> dict:
    result = compute_temperature_deviation_series(
        data_source=data_source,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        station_ids=station_ids,
        include_national=include_national,
    )
    return serialize_temperature_deviation_result(result)
