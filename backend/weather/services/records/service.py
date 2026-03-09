from weather.services.records.protocols import RecordsDataSource
from weather.services.records.types import RecordPoint


def ComputeRecords(data_source: RecordsDataSource, query) -> list[RecordPoint]:
    return data_source.fetch_records(query)
