from __future__ import annotations

from .protocols import RecordsGraphDataSource
from .types import RecordsGraphRequest, RecordsGraphResult


def get_records_graph(
    *,
    request: RecordsGraphRequest,
    data_source: RecordsGraphDataSource,
) -> RecordsGraphResult:
    if request.period_type == "month" and request.month is None:
        raise ValueError("month is required when period_type is 'month'")
    if request.period_type == "season" and request.season is None:
        raise ValueError("season is required when period_type is 'season'")
    if request.date_start > request.date_end:
        raise ValueError("date_start must be before or equal to date_end")

    return data_source.fetch_graph(request)
