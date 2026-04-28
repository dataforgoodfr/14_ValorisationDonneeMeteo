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


@dataclass(frozen=True)
class MinMaxOverviewQuery:
    date_start: dt.date
    date_end: dt.date
    type: str = "tmax"
    station_ids: tuple[str, ...] = ()
    station_search: str | None = None
    tmean_min: float | None = None
    tmean_max: float | None = None
    textreme_min: float | None = None
    textreme_max: float | None = None
    alt_min: float | None = None
    alt_max: float | None = None
    classe_recente_min: int | None = None
    classe_recente_max: int | None = None
    date_de_creation_min: dt.date | None = None
    date_de_creation_max: dt.date | None = None
    date_de_fermeture_min: dt.date | None = None
    date_de_fermeture_max: dt.date | None = None
    departments: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()
    ordering: str = "-textreme_mean"
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class MinMaxOverviewStation:
    station_id: str
    station_name: str
    textreme_mean: float
    tmean_mean: float
    lat: float | None
    lon: float | None
    alt: float | None
    department: str | None
    region: str | None
    classe: int | None
    annee_de_creation: int | None
    annee_de_fermeture: int | None


@dataclass(frozen=True)
class Pagination:
    total_count: int
    limit: int
    offset: int


@dataclass(frozen=True)
class MinMaxOverviewResult:
    pagination: Pagination
    stations: list[MinMaxOverviewStation]
