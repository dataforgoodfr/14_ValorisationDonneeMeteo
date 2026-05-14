from __future__ import annotations

from .protocols import TemperatureRecordsDataSource
from .types import (
    TemperatureRecordsRequest,
    TemperatureRecordsResult,
)


def get_temperature_records(
    *,
    request: TemperatureRecordsRequest,
    data_source: TemperatureRecordsDataSource,
) -> TemperatureRecordsResult:
    return data_source.fetch_records(request)
