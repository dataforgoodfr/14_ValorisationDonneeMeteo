from __future__ import annotations

from typing import Protocol

from .types import AbsoluteRecordsGraphResult, RecordsGraphRequest, RecordsGraphResult


class RecordsGraphDataSource(Protocol):
    def fetch_graph(self, request: RecordsGraphRequest) -> RecordsGraphResult: ...


class AbsoluteRecordsGraphDataSource(Protocol):
    def fetch_graph(
        self, request: RecordsGraphRequest
    ) -> AbsoluteRecordsGraphResult: ...
