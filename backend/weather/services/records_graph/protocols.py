from __future__ import annotations

from typing import Protocol

from .types import RecordsGraphRequest, RecordsGraphResult


class RecordsGraphDataSource(Protocol):
    def fetch_graph(self, request: RecordsGraphRequest) -> RecordsGraphResult: ...
