from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class RecordsGraphRequest:
    date_start: dt.date
    date_end: dt.date
    granularity: str  # "day" | "month" | "year"
    period_type: str  # "all_time" | "month" | "season"
    type_records: str  # "hot" | "cold"
    month: int | None = None
    season: str | None = None
    territoire: str | None = None  # "france" | "region" | "department" | "station"
    territoire_id: str | None = None


@dataclass(frozen=True)
class RecordsGraphBucket:
    bucket: str  # formatted date string (YYYY-MM-DD / YYYY-MM / YYYY)
    nb_records_battus: int
