import datetime as dt

from weather.services.records.protocols import (
    RecordsDataSource,
)
from weather.services.records.service import compute_records
from weather.services.records.types import StationRecords


def get_records(
    *,
    data_source: RecordsDataSource,
    date_start: dt.date,
    date_end: dt.date,
    station_ids: list[str] | tuple[str, ...] | None = None,
    record_kind: str = "absolute",
    record_scope: str = "all_time",
    type_records: str = "all",
) -> tuple[StationRecords, ...]:
    return compute_records(
        data_source=data_source,
        date_start=date_start,
        date_end=date_end,
        station_ids=station_ids,
        record_kind=record_kind,
        record_scope=record_scope,
        type_records=type_records,
    )
