from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from itertools import groupby

from weather.models import Quotidienne
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
from weather.services.national_indicator.types import DailyPoint


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


def _compute_itn_for_day(day: dt.date, mapping: dict[str, float]) -> float | None:
    expected = expected_station_codes(day)
    reims_expected = expected_reims_code(day)
    reims_other = REIMS_PRUNAY if reims_expected == REIMS_COURCY else REIMS_COURCY

    # Normalisation : ignorer l'autre Reims si elle existe
    if reims_other in mapping:
        mapping = dict(mapping)
        mapping.pop(reims_other)

    # Égalité stricte sur les 30 slots
    if set(mapping.keys()) != expected:
        return None

    return sum(mapping[c] for c in expected) / 30.0


class TimescaleNationalIndicatorDailyDataSource(NationalIndicatorDailyDataSource):
    """
    DataSource "réelle" : lit Quotidienne(tntxm) et produit une série nationale journalière.
    - Drop si jour incomplet (29 always + Reims attendu).
    - Baseline: stub (pipot) pour l'instant.
    """

    def __init__(self, *, baseline: BaselineStub | None = None) -> None:
        self._baseline = baseline or BaselineStub()

    def fetch_daily_series(
        self,
        *,
        date_start: dt.date,
        date_end: dt.date,
    ) -> list[DailyPoint]:
        rows = (
            Quotidienne.objects.filter(
                date__gte=date_start,
                date__lte=date_end,
                station__code__in=ITN_STATION_CODES_FOR_QUERY,
                tntxm__isnull=False,
            )
            .values_list("date", "station__code", "tntxm")
            .order_by("date", "station__code")
        )

        out: list[DailyPoint] = []

        # rows: Iterable[tuple[date, str, float]]
        for day, day_rows in groupby(rows, key=lambda r: r[0]):
            mapping: dict[str, float] = {}
            for _, station_code, tntxm in day_rows:
                # en cas de doublon station/jour, on écrase (ne devrait pas arriver)
                mapping[str(station_code)] = float(tntxm)

            itn = _compute_itn_for_day(day, mapping)
            if itn is None:
                continue  # drop le point

            b = self._baseline
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
