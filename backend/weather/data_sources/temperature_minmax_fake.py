from __future__ import annotations

import datetime as dt
import hashlib
import math
import random

from weather.services.temperature_minmax.protocols import (
    MinMaxGraphDataSource,
    MinMaxOverviewDataSource,
)
from weather.services.temperature_minmax.types import (
    DailyMinMaxPoint,
    MinMaxGraphQuery,
    MinMaxOverviewQuery,
    MinMaxOverviewResult,
    MinMaxOverviewStation,
    StationDailyMinMaxSeries,
)
from weather.services.temperature_minmax.types import Pagination as MinMaxPagination
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


_FAKE_OVERVIEW_STATIONS = [
    MinMaxOverviewStation(
        station_id="07149",
        station_name="Marseille-Marignane",
        textreme_mean=29.8,
        tmean_mean=16.2,
        lat=43.44,
        lon=5.22,
        alt=36.0,
        department="13",
        region="Provence-Alpes-Côte d'Azur",
        classe=1,
        annee_de_creation=1922,
        annee_de_fermeture=None,
    ),
    MinMaxOverviewStation(
        station_id="07222",
        station_name="Lyon-Bron",
        textreme_mean=26.3,
        tmean_mean=13.8,
        lat=45.73,
        lon=5.08,
        alt=200.0,
        department="69",
        region="Auvergne-Rhône-Alpes",
        classe=1,
        annee_de_creation=1921,
        annee_de_fermeture=None,
    ),
    MinMaxOverviewStation(
        station_id="07156",
        station_name="Paris-Montsouris",
        textreme_mean=23.1,
        tmean_mean=12.5,
        lat=48.82,
        lon=2.34,
        alt=75.0,
        department="75",
        region="Île-de-France",
        classe=1,
        annee_de_creation=1872,
        annee_de_fermeture=None,
    ),
]


class FakeTemperatureMinMaxOverviewDataSource(MinMaxOverviewDataSource):
    def fetch_station_overview(
        self, query: MinMaxOverviewQuery
    ) -> MinMaxOverviewResult:
        stations = list(_FAKE_OVERVIEW_STATIONS)
        total = len(stations)
        page = stations[query.offset : query.offset + query.limit]
        return MinMaxOverviewResult(
            pagination=MinMaxPagination(
                total_count=total,
                limit=query.limit,
                offset=query.offset,
            ),
            stations=page,
        )
