import datetime as dt

from weather.services.national_indicator.protocols import (
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.service import compute_national_indicator


def get_national_indicator(
    *,
    observed_data_source: NationalIndicatorObservedDataSource,
    baseline_data_source: NationalIndicatorBaselineDataSource,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str = "full",
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> dict:
    return compute_national_indicator(
        observed_data_source=observed_data_source,
        baseline_data_source=baseline_data_source,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )
