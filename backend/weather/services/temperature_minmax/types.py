from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class MinMaxGraphQuery:
    date_start: dt.date
    date_end: dt.date
    granularity: str
    station_ids: tuple[str, ...] = ()
    departments: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()

    @property
    def has_station_filter(self) -> bool:
        return bool(self.station_ids)

    @property
    def has_territory_filter(self) -> bool:
        return bool(self.departments or self.regions)


@dataclass(frozen=True)
class DailyMinMaxPoint:
    date: dt.date
    tmin: float | None
    tmax: float | None


@dataclass(frozen=True)
class StationDailyMinMaxSeries:
    station_id: str
    station_name: str
    points: list[DailyMinMaxPoint]


@dataclass(frozen=True)
class MinMaxGraphPoint:
    date: dt.date
    tmin_mean: float
    tmax_mean: float


@dataclass(frozen=True)
class NationalMinMaxSeries:
    data: list[MinMaxGraphPoint]


@dataclass(frozen=True)
class StationMinMaxSeries:
    station_id: str
    station_name: str
    data: list[MinMaxGraphPoint]


@dataclass(frozen=True)
class MinMaxGraphResult:
    national: NationalMinMaxSeries | None
    stations: list[StationMinMaxSeries]
