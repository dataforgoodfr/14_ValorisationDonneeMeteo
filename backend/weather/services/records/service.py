from weather.services.records.protocols import RecordsDataSource
from weather.services.records.types import RecordPoint, RecordsQuery


def compute_records(
    data_source: RecordsDataSource, query: RecordsQuery
) -> list[RecordPoint]:
    return data_source.fetch_records(query)
