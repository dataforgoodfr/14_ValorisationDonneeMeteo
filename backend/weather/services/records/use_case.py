import datetime as dt

from weather.services.records.protocols import (
    RecordsDataSource,
)
from weather.services.records.types import RecordPoint, RecordsQuery


def get_records(
    *,
    data_source: RecordsDataSource,
    date_start: dt.date,
    date_end: dt.date,
    station_name_filter: str | None = None,
    departement_filter: str | None = None,
) -> list[RecordPoint] | None:
    query = RecordsQuery(
        date_start=date_start,
        date_end=date_end,
        station_name_filter=station_name_filter,
        departement_filter=departement_filter,
    )

    # // Faire fonction fausses données
    # // Test unitaire - getrecord
    # // Test intégration -

    return compute_records(data_source, query)
