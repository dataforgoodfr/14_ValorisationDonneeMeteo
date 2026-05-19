from __future__ import annotations

from .protocols import AbsoluteRecordsGraphDataSource, RecordsGraphDataSource
from .types import AbsoluteRecordsGraphResult, RecordsGraphRequest, RecordsGraphResult


def get_records_graph(
    *,
    request: RecordsGraphRequest,
    data_source: RecordsGraphDataSource,
) -> RecordsGraphResult:
    if request.date_start > request.date_end:
        raise ValueError("date_start must be before or equal to date_end")

    return data_source.fetch_graph(request)


def get_absolute_records_graph(
    *,
    request: RecordsGraphRequest,
    data_source: AbsoluteRecordsGraphDataSource,
) -> AbsoluteRecordsGraphResult:
    if request.date_start > request.date_end:
        raise ValueError("date_start must be before or equal to date_end")

    return data_source.fetch_graph(request)
