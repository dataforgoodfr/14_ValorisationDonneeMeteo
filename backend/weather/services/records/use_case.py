import datetime as dt

from weather.services.records.protocols import (
    RecordsDataSource,
)


def get_records(
    *,
    data_source: RecordsDataSource,
    date_start: dt.date,
    date_end: dt.date,
    station_name_filter: str | None = None,
    departement_filter: str | None = None,
) -> dict | None:
    return None
