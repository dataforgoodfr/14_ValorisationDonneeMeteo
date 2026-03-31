from __future__ import annotations

from .protocols import TemperatureRecordsDataSource
from .types import TemperatureRecordEntry, TemperatureRecordsRequest


def get_temperature_records(
    *,
    request: TemperatureRecordsRequest,
    data_source: TemperatureRecordsDataSource,
) -> list[TemperatureRecordEntry]:
    """
    Valide la requête et délègue au data source.

    Raises ValueError si:
    - period_type == "month" et month est None
    - period_type == "season" et season est None
    """
    if request.period_type == "month" and request.month is None:
        raise ValueError("month is required when period_type is 'month'")

    if request.period_type == "season" and request.season is None:
        raise ValueError("season is required when period_type is 'season'")

    return data_source.fetch_records(request)
