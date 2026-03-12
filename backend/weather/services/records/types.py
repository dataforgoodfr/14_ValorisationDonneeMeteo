import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class RecordPoint:
    id: str
    name: str
    tnn: float
    txx: float
    tnn_date: dt.date | None = None
    txx_date: dt.date | None = None


@dataclass(frozen=True)
class RecordsQuery:
    date_start: dt.date
    date_end: dt.date

    station_name_filter: str | None
    departement_filter: str | None
