from __future__ import annotations

import datetime as dt
import hashlib
import math
import random

from weather.services.records.protocols import RecordsDataSource
from weather.services.records.types import (
    RecordsQuery,
    StationRecords,
    TemperatureRecord,
)


def _stable_int_from_str(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _seasonal_baseline_for_date(d: dt.date) -> tuple[float, float]:
    doy = d.timetuple().tm_yday
    phi = 2.0 * math.pi * (doy - 15) / 365.25

    mean_annual = 13.0
    amplitude = 10.0
    baseline_mean = mean_annual + amplitude * math.sin(phi)

    spread_base = 4.0
    spread_amp = 1.5
    spread = spread_base + spread_amp * (1 - math.sin(phi)) / 2.0

    return baseline_mean, spread


def _clamp_date(d: dt.date, date_start: dt.date, date_end: dt.date) -> dt.date:
    if d < date_start:
        return date_start
    if d > date_end:
        return date_end
    return d


def _season_start_dates(year: int) -> tuple[dt.date, ...]:
    return (
        dt.date(year, 3, 1),  # spring
        dt.date(year, 6, 1),  # summer
        dt.date(year, 9, 1),  # autumn
        dt.date(year, 12, 1),  # winter
    )


def _candidate_dates(query: RecordsQuery) -> tuple[dt.date, ...]:
    start = query.date_start
    end = query.date_end

    if start > end:
        return ()

    if query.record_scope == "all_time":
        return (end,)

    if query.record_scope == "monthly":
        out: list[dt.date] = []
        year = start.year
        month = start.month
        while (year, month) <= (end.year, end.month):
            out.append(_clamp_date(dt.date(year, month, 15), start, end))
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
        return tuple(dict.fromkeys(out))

    if query.record_scope == "seasonal":
        out: list[dt.date] = []
        for year in range(start.year, end.year + 1):
            for d in _season_start_dates(year):
                out.append(_clamp_date(d, start, end))
        out = [d for d in out if start <= d <= end]
        return tuple(dict.fromkeys(out))

    raise ValueError(f"Unsupported record_scope: {query.record_scope}")


def _build_hot_records(
    *,
    dates: tuple[dt.date, ...],
    rng: random.Random,
    station_bias: float,
) -> tuple[TemperatureRecord, ...]:
    out: list[TemperatureRecord] = []
    previous_value: float | None = None

    for d in dates:
        baseline_mean, spread = _seasonal_baseline_for_date(d)
        candidate = baseline_mean + spread + station_bias + rng.random() * 1.5

        if previous_value is not None:
            candidate = max(candidate, previous_value + 0.1)

        value = round(candidate, 1)
        out.append(TemperatureRecord(value=value, date=d))
        previous_value = value

    return tuple(out)


def _build_cold_records(
    *,
    dates: tuple[dt.date, ...],
    rng: random.Random,
    station_bias: float,
) -> tuple[TemperatureRecord, ...]:
    out: list[TemperatureRecord] = []
    previous_value: float | None = None

    for d in dates:
        baseline_mean, spread = _seasonal_baseline_for_date(d)
        candidate = baseline_mean - spread + station_bias - rng.random() * 1.5

        if previous_value is not None:
            candidate = min(candidate, previous_value - 0.1)

        value = round(candidate, 1)
        out.append(TemperatureRecord(value=value, date=d))
        previous_value = value

    return tuple(out)


def _station_name(station_id: str) -> str:
    return f"Station {station_id}"


def _get_all_stations():
    return "07231149", "07937156"  # parce que j'aime l'Ardèche


class FakeRecordsDataSource(RecordsDataSource):
    def __init__(self) -> None:
        self._seed = 123

    def fetch_records(self, query: RecordsQuery) -> tuple[StationRecords, ...]:
        station_ids = query.station_ids or _get_all_stations()

        out: list[StationRecords] = []
        for station_id in station_ids:
            out.append(
                self._generate_station_records(station_id=station_id, query=query)
            )

        return tuple(out)

    def _generate_station_records(
        self,
        *,
        station_id: str,
        query: RecordsQuery,
    ) -> StationRecords:
        station_hash = _stable_int_from_str(station_id)
        station_seed = (self._seed * 1_000_003) ^ station_hash
        rng = random.Random(station_seed)

        station_bias = ((station_hash % 100) - 50) / 10.0
        dates = _candidate_dates(query)

        hot_records = _build_hot_records(
            dates=dates,
            rng=rng,
            station_bias=station_bias,
        )

        cold_records = _build_cold_records(
            dates=dates,
            rng=rng,
            station_bias=station_bias,
        )

        if query.record_kind == "absolute":
            hot_records = hot_records[-1:] if hot_records else ()
            cold_records = cold_records[-1:] if cold_records else ()

        if query.type_records == "hot":
            cold_records = ()
        elif query.type_records == "cold":
            hot_records = ()

        return StationRecords(
            id=station_id,
            name=_station_name(station_id),
            hot_records=hot_records,
            cold_records=cold_records,
        )
