from __future__ import annotations

from typing import Protocol

from .types import TemperatureRecordEntry, TemperatureRecordsRequest


class TemperatureRecordsDataSource(Protocol):
    def fetch_records(
        self, request: TemperatureRecordsRequest
    ) -> list[TemperatureRecordEntry]: ...
