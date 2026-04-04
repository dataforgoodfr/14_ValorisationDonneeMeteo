from __future__ import annotations

from typing import Protocol

from .types import RecordsGraphBucket, RecordsGraphRequest


class RecordsGraphDataSource(Protocol):
    def fetch_graph(self, request: RecordsGraphRequest) -> list[RecordsGraphBucket]: ...
