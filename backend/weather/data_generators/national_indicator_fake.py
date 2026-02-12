from __future__ import annotations

import datetime as dt
import math
import random

from weather.services.national_indicator.service import compute_national_indicator
from weather.services.national_indicator.types import DailyPoint
from weather.services.time_windows import iter_days_intersecting


class FakeNationalIndicatorDailyDataSource:
    def __init__(self, *, seed: int = 42) -> None:
        self._seed = seed

    def fetch_daily_series(
        self,
        *,
        date_start: dt.date,
        date_end: dt.date,
        seed: int | None = None,
    ) -> list[DailyPoint]:
        rng = random.Random(self._seed)
        out: list[DailyPoint] = []

        for d in iter_days_intersecting(date_start, date_end):
            baseline_mean, sigma, bmin, bmax = _climatology_for_date(d)
            temperature = baseline_mean + rng.gauss(0.0, sigma)

            out.append(
                DailyPoint(
                    date=d,
                    temperature=temperature,
                    baseline_mean=baseline_mean,
                    baseline_std_dev_upper=baseline_mean + sigma,
                    baseline_std_dev_lower=baseline_mean - sigma,
                    baseline_max=bmax,
                    baseline_min=bmin,
                )
            )

        return out


def _climatology_for_date(d: dt.date) -> tuple[float, float, float, float]:
    doy = d.timetuple().tm_yday
    phi = 2.0 * math.pi * (doy - 15) / 365.25

    mean_annual = 13.0
    amplitude = 6.0
    baseline_mean = mean_annual + amplitude * math.sin(phi)

    sigma_base = 1.6
    sigma_amp = 0.6
    sigma = sigma_base + sigma_amp * (1 - math.sin(phi)) / 2.0

    baseline_min = baseline_mean - (3.0 * sigma + 1.0)
    baseline_max = baseline_mean + (3.0 * sigma + 1.0)
    return baseline_mean, sigma, baseline_min, baseline_max


def generate_fake_national_indicator(
    *,
    date_start: dt.date,
    date_end: dt.date,
    granularity: str,
    slice_type: str = "full",
    month_of_year: int | None = None,
    day_of_month: int | None = None,
) -> dict:
    """
    Façade rétro-compatible : utilisée par les tests existants.
    """
    ds = FakeNationalIndicatorDailyDataSource(seed=42)
    return compute_national_indicator(
        data_source=ds,
        date_start=date_start,
        date_end=date_end,
        granularity=granularity,
        slice_type=slice_type,
        month_of_year=month_of_year,
        day_of_month=day_of_month,
    )
