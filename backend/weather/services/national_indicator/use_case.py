from __future__ import annotations

import datetime as dt

from weather.bootstrap_itn import ITNDependencyProvider


def get_national_indicator(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str = "full",
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> dict:
    """
    Use case ITN : orchestre la récupération de la datasource (DI) et exécute le calcul métier.
    Retourne la payload métier (ex: {"time_series": [...] }).
    """
    # Import local pour éviter les imports circulaires (bootstrap -> timescale -> services, etc.)
    from weather.services.national_indicator.service import compute_national_indicator

    ds = ITNDependencyProvider.get_dep()
    return compute_national_indicator(
        data_source=ds,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )
