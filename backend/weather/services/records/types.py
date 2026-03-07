import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class RecordPoint:
    id: str
    name: str
    TNN: float
    TXX: float
    TNN_date: dt.date
    TXX_date: dt.date


@dataclass(frozen=True)
class RecordsQuery:
    date_start: dt.date
    date_end: dt.date

    station_name_filter: str | None
    departement_filter: str | None
