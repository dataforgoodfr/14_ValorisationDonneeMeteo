import datetime as dt

from .protocols import RecordsDataSource
from .types import RecordsQuery, StationRecords


def compute_records(
    *,
    data_source: RecordsDataSource,
    date_start: dt.date | None = None,
    date_end: dt.date | None = None,
    station_ids: list[str] | tuple[str, ...] | None = None,
    departments: list[str] | tuple[str, ...] | None = None,
    record_kind: str = "absolute",
    record_scope: str = "all_time",
    type_records: str = "all",
    temperature_min: float | None = None,
    temperature_max: float | None = None,
) -> tuple[StationRecords, ...]:
    query = RecordsQuery(
        date_start=date_start,
        date_end=date_end,
        station_ids=tuple(station_ids or ()),
        departments=tuple(departments or ()),
        record_kind=record_kind,
        record_scope=record_scope,
        type_records=type_records,
        temperature_min=temperature_min,
        temperature_max=temperature_max,
    )

    return data_source.fetch_records(query)
