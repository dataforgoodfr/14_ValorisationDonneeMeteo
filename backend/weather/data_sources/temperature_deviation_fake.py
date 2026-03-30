from __future__ import annotations

import datetime as dt
import hashlib
import math
import random
from collections.abc import Iterable
from datetime import date

from weather.services.temperature_deviation.protocols import (
    TemperatureDeviationDailyDataSource,
)
from weather.services.temperature_deviation.types import (
    DailyDeviationPoint,
    DailyDeviationSeriesQuery,
    StationDailySeries,
)
from weather.utils.date_range import iter_days_intersecting


def _climatology_for_date(d: dt.date) -> tuple[float, float]:
    doy = d.timetuple().tm_yday
    phi = 2.0 * math.pi * (doy - 15) / 365.25

    mean_annual = 13.0
    amplitude = 6.0
    baseline_mean = mean_annual + amplitude * math.sin(phi)

    sigma_base = 1.6
    sigma_amp = 0.6
    sigma = sigma_base + sigma_amp * (1 - math.sin(phi)) / 2.0

    return baseline_mean, sigma


def _stable_int_from_str(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _generate_national_daily_point(
    *,
    day: dt.date,
    rng: random.Random,
) -> DailyDeviationPoint:
    baseline_mean, sigma = _climatology_for_date(day)
    temperature = baseline_mean + rng.gauss(0.0, sigma * 0.6)

    return DailyDeviationPoint(
        date=day,
        temperature=temperature,
        baseline_mean=baseline_mean,
    )


def _generate_station_daily_point(
    *,
    day: dt.date,
    rng: random.Random,
    bias: float,
) -> DailyDeviationPoint:
    baseline_mean, sigma = _climatology_for_date(day)
    temperature = baseline_mean + bias + rng.gauss(0.0, sigma)

    return DailyDeviationPoint(
        date=day,
        temperature=temperature,
        baseline_mean=baseline_mean,
    )


def _generate_station_series(
    *,
    station_id: str,
    days: Iterable[date],
    global_seed: int,
) -> list[DailyDeviationPoint]:
    station_hash = _stable_int_from_str(station_id)
    station_seed = (global_seed * 1_000_003) ^ station_hash
    rng = random.Random(station_seed)
    bias = ((station_hash % 100) - 50) / 200.0

    return [
        _generate_station_daily_point(
            day=d,
            rng=rng,
            bias=bias,
        )
        for d in days
    ]


class FakeTemperatureDeviationDailyDataSource(TemperatureDeviationDailyDataSource):
    def __init__(self) -> None:
        self._seed = 123

    def fetch_national_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[DailyDeviationPoint]:
        rng = random.Random(self._seed)
        days = tuple(iter_days_intersecting(query.date_start, query.date_end))

        out = [_generate_national_daily_point(day=d, rng=rng) for d in days]
        return out

    def fetch_stations_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[StationDailySeries]:
        days = tuple(iter_days_intersecting(query.date_start, query.date_end))
        out: list[StationDailySeries] = []

        for station_id in query.station_ids:
            points = _generate_station_series(
                station_id=station_id,
                days=days,
                global_seed=self._seed,
            )

            out.append(
                StationDailySeries(
                    station_id=station_id,
                    station_name=f"Station {station_id}",
                    points=points,
                )
            )

        return out
