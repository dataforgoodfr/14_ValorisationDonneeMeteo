from weather.services.records.protocols import RecordsDataSource
from weather.services.records.types import RecordPointSet, RecordsQuery


def compute_records(
    data_source: RecordsDataSource, query: RecordsQuery
) -> list[RecordPointSet]:
    return data_source.fetch_records(query)
