import datetime as dt
from dataclasses import dataclass


@dataclass
class RecordValue:
    valeur: float
    date: dt.date


@dataclass(frozen=True)
class RecordPointSet:
    id: str
    name: str
    records_chaud: list[RecordValue] | None = None
    records_froid: list[RecordValue] | None = None


@dataclass(frozen=True)
class RecordsQuery:
    date_start: dt.date
    date_end: dt.date

    station_name_filter: str | None
    departement_filter: str | None
