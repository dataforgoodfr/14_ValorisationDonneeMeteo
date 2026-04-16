from __future__ import annotations

import datetime as dt

from .protocols import MinMaxGraphDataSource
from .service import compute_minmax_graph
from .types import MinMaxGraphQuery


def get_minmax_graph(
    *,
    data_source: MinMaxGraphDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    station_ids: tuple[str, ...] = (),
    departments: tuple[str, ...] = (),
    regions: tuple[str, ...] = (),
) -> dict:
    query = MinMaxGraphQuery(
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        station_ids=station_ids,
        departments=departments,
        regions=regions,
    )
    return compute_minmax_graph(data_source=data_source, query=query)
