from __future__ import annotations

from typing import Protocol

from .types import (
    TemperatureRecordsRequest,
    TemperatureRecordsResult,
)


class TemperatureRecordsDataSource(Protocol):
    def fetch_records(
        self, request: TemperatureRecordsRequest
    ) -> TemperatureRecordsResult: ...
