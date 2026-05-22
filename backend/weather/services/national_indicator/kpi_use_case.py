from __future__ import annotations

import datetime as dt

from weather.services.national_indicator.protocols import (
    NationalIndicatorKpiDataSource,
)
from weather.services.national_indicator.types import NationalIndicatorKpiResult


def get_national_indicator_kpi(
    *,
    kpi_data_source: NationalIndicatorKpiDataSource,
    date_start: dt.date,
    date_end: dt.date,
) -> NationalIndicatorKpiResult:
    duration = date_end - date_start
    prev_date_end = date_start - dt.timedelta(days=1)
    prev_date_start = prev_date_end - duration
    return kpi_data_source.compute_kpi(
        current_start=date_start,
        current_end=date_end,
        previous_start=prev_date_start,
        previous_end=prev_date_end,
    )
