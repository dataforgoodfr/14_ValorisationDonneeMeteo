from __future__ import annotations

from .protocols import (
    TemperatureAbsoluteRecordsDataSource,
    TemperatureRecordsDataSource,
)
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


def get_temperature_absolute_records(
    *,
    request: TemperatureRecordsRequest,
    data_source: TemperatureAbsoluteRecordsDataSource,
) -> TemperatureRecordsResult:
    return data_source.fetch_records(request)
