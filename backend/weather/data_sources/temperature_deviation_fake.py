from __future__ import annotations

import datetime as dt
import hashlib
import math
import random
from collections.abc import Iterable
from datetime import date

from weather.services.temperature_deviation.protocols import (
    TemperatureDeviationDailyDataSource,
    TemperatureDeviationOverviewDataSource,
)
from weather.services.temperature_deviation.types import (
    DailyBaselinePoint,
    DailyDeviationPoint,
    DailyDeviationSeriesQuery,
    MonthlyBaselinePoint,
    ObservedPoint,
    Pagination,
    StationDailySeries,
    TemperatureDeviationOverviewQuery,
    TemperatureDeviationOverviewResult,
    TemperatureDeviationOverviewStation,
    YearlyBaselinePoint,
)
from weather.utils.date_range import iter_days_intersecting

_CREATION_YEAR_POOL = (1950, 1960, 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010)


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


def _generate_national_observed_point(
    *,
    day: dt.date,
    rng: random.Random,
) -> ObservedPoint:
    baseline_mean, sigma = _climatology_for_date(day)
    temperature = baseline_mean + rng.gauss(0.0, sigma * 0.6)

    return ObservedPoint(
        date=day,
        temperature=temperature,
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


def _fake_daily_baseline() -> list[DailyBaselinePoint]:
    year = 2000
    start = dt.date(year, 1, 1)
    end = dt.date(year, 12, 31)

    out: list[DailyBaselinePoint] = []
    for day in iter_days_intersecting(start, end):
        baseline_mean, _ = _climatology_for_date(day)
        out.append(
            DailyBaselinePoint(
                month=day.month,
                day_of_month=day.day,
                mean=baseline_mean,
            )
        )
    return out


def _fake_monthly_baseline() -> list[MonthlyBaselinePoint]:
    daily = _fake_daily_baseline()
    by_month: dict[int, list[float]] = {}

    for p in daily:
        by_month.setdefault(p.month, []).append(p.mean)

    return [
        MonthlyBaselinePoint(
            month=month,
            mean=sum(values) / len(values),
        )
        for month, values in sorted(by_month.items())
    ]


def _fake_yearly_baseline() -> YearlyBaselinePoint:
    daily = _fake_daily_baseline()
    return YearlyBaselinePoint(mean=sum(p.mean for p in daily) / len(daily))


class FakeTemperatureDeviationDailyDataSource(TemperatureDeviationDailyDataSource):
    def __init__(self) -> None:
        self._seed = 123

    def fetch_national_observed_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[ObservedPoint]:
        rng = random.Random(self._seed)
        if query.target_dates is not None:
            days = tuple(sorted(query.target_dates))
        else:
            days = tuple(iter_days_intersecting(query.date_start, query.date_end))

        return [_generate_national_observed_point(day=d, rng=rng) for d in days]

    def fetch_stations_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[StationDailySeries]:
        if query.target_dates is not None:
            days = tuple(sorted(query.target_dates))
        else:
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

    def fetch_national_daily_baseline(self) -> list[DailyBaselinePoint]:
        return _fake_daily_baseline()

    def fetch_national_monthly_baseline(self) -> list[MonthlyBaselinePoint]:
        return _fake_monthly_baseline()

    def fetch_national_yearly_baseline(self) -> YearlyBaselinePoint | None:
        return _fake_yearly_baseline()


class FakeTemperatureDeviationOverviewDataSource(
    TemperatureDeviationOverviewDataSource
):
    def __init__(self) -> None:
        self._seed = 123
        self._stations = self._build_dataset()

    def _build_dataset(self) -> list[TemperatureDeviationOverviewStation]:
        out = []
        rng = random.Random(self._seed)
        departments = ["75", "13", "69", "31", "59"]

        def department_to_region(dep: str) -> str:
            mapping = {
                "75": "Île-de-France",
                "13": "Provence-Alpes-Côte d'Azur",
                "69": "Auvergne-Rhône-Alpes",
                "31": "Occitanie",
                "59": "Hauts-de-France",
            }
            return mapping.get(dep, "Autre")

        for i in range(500):
            station_id = f"{70000 + i}"
            department = departments[i % len(departments)]

            temperature_mean = rng.uniform(5, 30)
            baseline_mean = temperature_mean - rng.uniform(-3, 3)
            deviation = temperature_mean - baseline_mean

            creation_year = _CREATION_YEAR_POOL[i % len(_CREATION_YEAR_POOL)]

            out.append(
                TemperatureDeviationOverviewStation(
                    station_id=station_id,
                    station_name=f"Station {station_id}",
                    lat=40.0 + (i % 50) * 0.1,
                    lon=-5.0 + (i % 80) * 0.1,
                    department=department,
                    alt=50 + (i % 200),
                    region=department_to_region(department),
                    temperature_mean=temperature_mean,
                    baseline_mean=baseline_mean,
                    deviation=deviation,
                    classe_recente=1,
                    date_de_creation=dt.date(creation_year, 1, 1),
                    date_de_fermeture=None,
                )
            )

        return out

    def fetch_national_mean_deviation(
        self,
        *,
        date_start,
        date_end,
    ) -> float:
        # valeur fixe simple
        return 1.5

    def fetch_station_overview(
        self,
        query: TemperatureDeviationOverviewQuery,
    ) -> TemperatureDeviationOverviewResult:
        data = self._stations

        if query.station_ids:
            allowed = set(query.station_ids)
            data = [x for x in data if x.station_id in allowed]

        if query.station_search:
            s = query.station_search.lower()
            data = [x for x in data if s in x.station_name.lower()]

        if query.departments:
            allowed = set(query.departments)
            data = [x for x in data if x.department in allowed]

        if query.regions:
            allowed = set(query.regions)
            data = [x for x in data if x.region in allowed]

        if query.alt_min is not None:
            data = [x for x in data if x.alt is not None and x.alt >= query.alt_min]

        if query.alt_max is not None:
            data = [x for x in data if x.alt is not None and x.alt <= query.alt_max]

        if query.temperature_mean_min is not None:
            data = [x for x in data if x.temperature_mean >= query.temperature_mean_min]

        if query.temperature_mean_max is not None:
            data = [x for x in data if x.temperature_mean <= query.temperature_mean_max]

        if query.deviation_min is not None:
            data = [x for x in data if x.deviation >= query.deviation_min]

        if query.deviation_max is not None:
            data = [x for x in data if x.deviation <= query.deviation_max]

        reverse = query.ordering.startswith("-")
        field = query.ordering.lstrip("-")

        def key(x):
            return getattr(x, field)

        data = sorted(data, key=key, reverse=reverse)
        total_count = len(data)

        start = query.offset
        end = start + query.limit

        page_items = data[start:end]

        return TemperatureDeviationOverviewResult(
            national_deviation_mean=1.5,  # ignoré ici
            pagination=Pagination(
                total_count=total_count,
                limit=query.limit,
                offset=query.offset,
            ),
            stations=page_items,
        )
