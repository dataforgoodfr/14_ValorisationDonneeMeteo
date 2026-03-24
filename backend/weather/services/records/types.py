import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class TemperatureRecord:
    value: float
    date: dt.date


@dataclass(frozen=True)
class StationRecords:
    id: str
    name: str
    hot_records: tuple[TemperatureRecord, ...]
    cold_records: tuple[TemperatureRecord, ...]


@dataclass(frozen=True)
class RecordsQuery:
    date_start: dt.date | None
    date_end: dt.date | None
    station_ids: tuple[str, ...]
    departments: tuple[str, ...]
    record_kind: str  # "historical" | "absolute"
    record_scope: str  # "monthly" | "seasonal" | "all_time"
    type_records: str  # "hot" | "cold" | "all"
    temperature_min: float | None
    temperature_max: float | None
