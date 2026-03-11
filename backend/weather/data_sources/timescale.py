from __future__ import annotations

import datetime as dt
from collections import defaultdict
from dataclasses import dataclass

from weather.models import QuotidienneITN
from weather.services.national_indicator.protocols import (
    NationalIndicatorDailyDataSource,
)
from weather.services.national_indicator.stations import (
    ITN_STATION_CODES_FOR_QUERY,
    REIMS_COURCY,
    REIMS_PRUNAY,
    expected_reims_code,
    expected_station_codes,
)
from weather.services.national_indicator.types import DailyPoint, DailySeriesQuery


def _normalize_reims(
    day: dt.date, station_code_to_temp_map: dict[str, float]
) -> dict[str, float]:
    reims_expected = expected_reims_code(day)
    reims_other = REIMS_PRUNAY if reims_expected == REIMS_COURCY else REIMS_COURCY

    if reims_other not in station_code_to_temp_map:
        return station_code_to_temp_map

    m = dict(station_code_to_temp_map)
    m.pop(reims_other, None)
    return m


@dataclass(frozen=True)
class BaselineStub:
    """
    Baseline "pipot" temporaire.
    A remplacer par une vraie climato plus tard, quand on saura comment calculer la baseline 1991-2020
    """

    mean: float = 0.0
    std_upper: float = 0.0
    std_lower: float = 0.0
    max_: float = 0.0
    min_: float = 0.0

    def mean_for(self, temperature: float) -> float:
        # écart=1 (parce que pourquoi pas) => baseline_mean == temperature - 1
        return temperature - 1


def compute_itn_for_day(
    day: dt.date, station_code_to_temp_map: dict[str, float]
) -> float | None:
    expected_stations_for_day = expected_station_codes(day)
    if len(expected_stations_for_day) != 30:
        raise ValueError(
            f"Expected 30 stations, got {len(expected_stations_for_day)} for {day}"
        )
    # Normalisation : ignorer l'autre Reims si elle existe
    station_code_to_temp_map = _normalize_reims(day, station_code_to_temp_map)
    # Égalité stricte sur les 30 slots
    computed_stations_codes = set(station_code_to_temp_map.keys())

    if computed_stations_codes != expected_stations_for_day:
        return None

    return sum(station_code_to_temp_map[c] for c in expected_stations_for_day) / float(
        len(expected_stations_for_day)
    )


class TimescaleNationalIndicatorDailyDataSource(NationalIndicatorDailyDataSource):
    """
    DataSource "réelle" : lit Quotidienne(tntxm) et produit une série nationale journalière.
    - Drop si jour incomplet (29 always + Reims attendu).
    - Baseline: stub (pipot) pour l'instant.
    """

    def __init__(self, *, baseline: BaselineStub | None = None) -> None:
        self._baseline = baseline or BaselineStub()

    def fetch_daily_series(self, query: DailySeriesQuery) -> list[DailyPoint]:
        qs = QuotidienneITN.objects.filter(
            date__gte=query.date_start,
            date__lte=query.date_end,
            station_code__in=ITN_STATION_CODES_FOR_QUERY,
        )

        if query.target_dates is not None:
            qs = qs.filter(date__in=query.target_dates)

        rows = (
            qs.order_by("date", "station_code")
            .values_list("date", "station_code", "tntxm")
            .iterator(chunk_size=10_000)
        )

        # day -> {station_code -> tntxm}
        by_day: dict[dt.date, dict[str, float]] = defaultdict(dict)

        for day, station_code, tntxm in rows:
            code = str(station_code)
            station_code_to_temp_map = by_day[day]
            if code in station_code_to_temp_map:
                raise ValueError(
                    f"Duplicate station/day in v_quotidienne_itn: station_code={code}, date={day}"
                )
            station_code_to_temp_map[code] = float(tntxm)

        out: list[DailyPoint] = []
        b = self._baseline

        for day in sorted(by_day.keys()):
            itn = compute_itn_for_day(day, by_day[day])
            if itn is None:
                continue

            out.append(
                DailyPoint(
                    date=day,
                    temperature=itn,
                    baseline_mean=b.mean_for(itn),
                    baseline_std_dev_upper=b.std_upper,
                    baseline_std_dev_lower=b.std_lower,
                    baseline_max=b.max_,
                    baseline_min=b.min_,
                )
            )

        return out
