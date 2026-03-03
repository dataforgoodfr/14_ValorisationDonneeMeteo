from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class DailyPoint:
    date: dt.date
    temperature: float
    baseline_mean: float
    baseline_std_dev_upper: float
    baseline_std_dev_lower: float
    baseline_max: float
    baseline_min: float


@dataclass(frozen=True)
class OutputPoint:
    date: dt.date
    temperature: float
    baseline_mean: float
    baseline_std_dev_upper: float
    baseline_std_dev_lower: float
    baseline_max: float
    baseline_min: float


@dataclass(frozen=True)
class DailySeriesQuery:
    date_start: dt.date
    date_end: dt.date
    # Dates exactes à récupérer (si slice => on veut réduire la volumétrie DB)
    # Si None: fallback "fenêtre complète".
    target_dates: tuple[dt.date, ...] | None = None
