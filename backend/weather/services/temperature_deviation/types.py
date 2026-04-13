from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class ObservedPoint:
    date: dt.date
    temperature: float


@dataclass(frozen=True)
class DailyDeviationSeriesQuery:
    date_start: dt.date
    date_end: dt.date
    station_ids: tuple[str, ...]
    include_national: bool = True


@dataclass(frozen=True)
class DailyDeviationPoint:
    date: dt.date
    temperature: float
    baseline_mean: float


@dataclass(frozen=True)
class StationDailySeries:
    station_id: str
    station_name: str
    points: list[DailyDeviationPoint]


@dataclass(frozen=True)
class AggregatedDeviationPoint:
    date: dt.date
    temperature: float
    baseline_mean: float

    @property
    def deviation(self) -> float:
        return self.temperature - self.baseline_mean


@dataclass(frozen=True)
class NationalDeviationSeries:
    data: list[AggregatedDeviationPoint]


@dataclass(frozen=True)
class StationDeviationSeries:
    station_id: str
    station_name: str
    data: list[AggregatedDeviationPoint]


@dataclass(frozen=True)
class TemperatureDeviationResult:
    national: NationalDeviationSeries | None
    stations: list[StationDeviationSeries]


@dataclass(frozen=True)
class DailyBaselinePoint:
    month: int
    day_of_month: int
    mean: float


@dataclass(frozen=True)
class MonthlyBaselinePoint:
    month: int
    mean: float


@dataclass(frozen=True)
class YearlyBaselinePoint:
    mean: float


@dataclass(frozen=True)
class TemperatureDeviationOverviewQuery:
    date_start: dt.date
    date_end: dt.date
    station_ids: tuple[str, ...] = ()
    station_search: str | None = None
    temperature_mean_min: float | None = None
    temperature_mean_max: float | None = None
    deviation_min: float | None = None
    deviation_max: float | None = None
    ordering: str = "-deviation"
    limit: int = 50
    offset: int = 0
    alt_min: float | None = None
    alt_max: float | None = None
    departments: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemperatureDeviationOverviewStation:
    station_id: str
    station_name: str
    temperature_mean: float
    baseline_mean: float
    deviation: float
    lat: float | None
    lon: float | None
    alt: float | None
    department: str | None
    region: str | None


@dataclass(frozen=True)
class Pagination:
    total_count: int
    limit: int
    offset: int


@dataclass(frozen=True)
class TemperatureDeviationOverviewResult:
    national_deviation_mean: float
    pagination: Pagination
    stations: list[TemperatureDeviationOverviewStation]
