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
