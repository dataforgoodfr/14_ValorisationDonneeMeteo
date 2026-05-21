from __future__ import annotations

import datetime as dt

from .protocols import ExtremesGraphDataSource
from .service import compute_extremes_graph
from .types import ExtremesGraphQuery


def get_extremes_graph(
    *,
    data_source: ExtremesGraphDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    station_ids: tuple[str, ...] = (),
    departments: tuple[str, ...] = (),
    regions: tuple[str, ...] = (),
) -> dict:
    query = ExtremesGraphQuery(
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        station_ids=station_ids,
        departments=departments,
        regions=regions,
    )
    return compute_extremes_graph(data_source=data_source, query=query)
