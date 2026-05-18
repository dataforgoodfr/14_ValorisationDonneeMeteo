from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtremesGraphQuery:
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
class DailyExtremesPoint:
    date: dt.date
    tn: float | None
    tx: float | None


@dataclass(frozen=True)
class StationDailyExtremesSeries:
    station_id: str
    station_name: str
    points: list[DailyExtremesPoint]


@dataclass(frozen=True)
class ExtremesGraphPoint:
    date: dt.date
    tnm: float
    txm: float


@dataclass(frozen=True)
class NationalExtremesSeries:
    data: list[ExtremesGraphPoint]


@dataclass(frozen=True)
class StationExtremesSeries:
    station_id: str
    station_name: str
    data: list[ExtremesGraphPoint]


@dataclass(frozen=True)
class ExtremesGraphResult:
    national: NationalExtremesSeries | None
    stations: list[StationExtremesSeries]


@dataclass(frozen=True)
class ExtremesOverviewQuery:
    date_start: dt.date
    date_end: dt.date
    type: str = "tx"
    station_ids: tuple[str, ...] = ()
    station_search: str | None = None
    tmean_min: float | None = None
    tmean_max: float | None = None
    txn: float | None = None
    txx: float | None = None
    tnn: float | None = None
    tnx: float | None = None
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
    ordering: str = "-txm"
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class ExtremesOverviewStation:
    station_id: str
    station_name: str
    txm: float
    tnm: float
    tmm: float
    lat: float | None
    lon: float | None
    alt: float | None
    department: str | None
    region: str | None
    classe_recente: int | None
    date_de_creation: dt.date
    date_de_fermeture: dt.date | None


@dataclass(frozen=True)
class Pagination:
    total_count: int
    limit: int
    offset: int


@dataclass(frozen=True)
class ExtremesOverviewResult:
    pagination: Pagination
    stations: list[ExtremesOverviewStation]
