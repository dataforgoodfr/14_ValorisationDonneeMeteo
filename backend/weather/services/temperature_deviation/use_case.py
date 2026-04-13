from __future__ import annotations

import datetime as dt

from .protocols import (
    TemperatureDeviationDailyDataSource,
    TemperatureDeviationOverviewDataSource,
)
from .service import (
    compute_temperature_deviation,
    compute_temperature_deviation_overview,
)


def get_temperature_deviation(
    *,
    data_source: TemperatureDeviationDailyDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    station_ids: tuple[str, ...] = (),
    include_national: bool = True,
) -> dict:
    return compute_temperature_deviation(
        data_source=data_source,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        station_ids=station_ids,
        include_national=include_national,
    )


def get_temperature_deviation_overview(
    *,
    data_source: TemperatureDeviationOverviewDataSource,
    date_start: dt.date,
    date_end: dt.date,
    station_ids: tuple[str, ...] = (),
    station_search: str | None = None,
    temperature_mean_min: float | None = None,
    temperature_mean_max: float | None = None,
    deviation_min: float | None = None,
    deviation_max: float | None = None,
    alt_min: float | None = None,
    alt_max: float | None = None,
    departments: tuple[str, ...] = (),
    regions: tuple[str, ...] = (),
    ordering: str = "-deviation",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    return compute_temperature_deviation_overview(
        data_source=data_source,
        date_start=date_start,
        date_end=date_end,
        station_ids=station_ids,
        station_search=station_search,
        temperature_mean_min=temperature_mean_min,
        temperature_mean_max=temperature_mean_max,
        deviation_min=deviation_min,
        deviation_max=deviation_max,
        alt_min=alt_min,
        alt_max=alt_max,
        departments=departments,
        regions=regions,
        ordering=ordering,
        limit=limit,
        offset=offset,
    )
