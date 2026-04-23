from __future__ import annotations

import datetime as dt
import hashlib
import math
import random

from weather.services.temperature_minmax.protocols import MinMaxGraphDataSource
from weather.services.temperature_minmax.types import (
    DailyMinMaxPoint,
    MinMaxGraphQuery,
    StationDailyMinMaxSeries,
)
from weather.utils.date_range import iter_days_intersecting

FAKE_STATION_IDS = ["07149", "07222", "07460", "07481", "07630"]


def _seasonal_mean(d: dt.date) -> float:
    doy = d.timetuple().tm_yday
    phi = 2.0 * math.pi * (doy - 15) / 365.25
    return 13.0 + 8.0 * math.sin(phi)


def _stable_int(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest()[:16], 16)


def _generate_point(d: dt.date, rng: random.Random, bias: float) -> DailyMinMaxPoint:
    mean = _seasonal_mean(d)
    tmin = mean - 4.0 + bias + rng.gauss(0.0, 1.5)
    tmax = mean + 4.0 + bias + rng.gauss(0.0, 1.5)
    return DailyMinMaxPoint(
        date=d,
        tmin=round(tmin, 1),
        tmax=round(tmax, 1),
    )


class FakeTemperatureMinMaxDataSource(MinMaxGraphDataSource):
    def __init__(self) -> None:
        self._seed = 42

    def fetch_daily_series(
        self, query: MinMaxGraphQuery
    ) -> list[StationDailyMinMaxSeries]:
        if query.station_ids:
            station_ids = list(query.station_ids)
        else:
            station_ids = FAKE_STATION_IDS[:3]

        days = list(iter_days_intersecting(query.date_start, query.date_end))
        result = []

        for station_id in station_ids:
            station_hash = _stable_int(station_id)
            rng = random.Random((self._seed * 1_000_003) ^ station_hash)
            bias = ((station_hash % 100) - 50) / 100.0

            result.append(
                StationDailyMinMaxSeries(
                    station_id=station_id,
                    station_name=f"Station {station_id}",
                    points=[_generate_point(d, rng, bias) for d in days],
                )
            )

        return result

    def fetch_national_daily_series(
        self, query: MinMaxGraphQuery
    ) -> list[DailyMinMaxPoint]:
        days = list(iter_days_intersecting(query.date_start, query.date_end))
        rng = random.Random(self._seed)
        return [_generate_point(d, rng, 0.0) for d in days]
