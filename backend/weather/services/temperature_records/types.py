from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

SEASON_MONTHS: dict[str, list[int]] = {
    "winter": [12, 1, 2],
    "spring": [3, 4, 5],
    "summer": [6, 7, 8],
    "autumn": [9, 10, 11],
}


@dataclass(frozen=True)
class TemperatureRecordsRequest:
    period_type: str  # "month" | "season" | "all_time"
    type_records: str  # "hot" | "cold"
    month: int | None = None
    season: str | None = None
    date_start: dt.date | None = None
    date_end: dt.date | None = None
    territoire: str | None = None  # "france" | "region" | "department" | "station"
    territoire_id: str | None = None


@dataclass(frozen=True)
class TemperatureRecordEntry:
    station_id: str
    station_name: str
    department: str
    record_value: float
    record_date: dt.date
    lat: float
    lon: float
    alt: float
    classe_recente: int
    date_de_creation: dt.date
    date_de_fermeture: dt.date | None
