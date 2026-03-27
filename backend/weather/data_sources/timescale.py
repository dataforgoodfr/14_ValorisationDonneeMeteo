from __future__ import annotations

import datetime as dt
from collections import defaultdict

from django.db.models import OuterRef, Subquery
from django.db.models.functions import ExtractDay, ExtractMonth

from weather.models import (
    BaselineStationDailyMean19912020,
    ITNBaselineDaily19912020,
    ITNBaselineMonthly19912020,
    ITNBaselineYearly19912020,
    QuotidienneITN,
    Station,
)
from weather.services.national_indicator.protocols import (
    NationalIndicatorBaselineDataSource,
    NationalIndicatorObservedDataSource,
)
from weather.services.national_indicator.stations import (
    ITN_STATION_CODES_FOR_QUERY,
    REIMS_COURCY,
    REIMS_PRUNAY,
    expected_reims_code,
    expected_station_codes,
)
from weather.services.national_indicator.types import (
    BaselinePoint,
    DailySeriesQuery,
    ObservedPoint,
)
from weather.services.temperature_deviation.protocols import (
    TemperatureDeviationDailyDataSource,
)
from weather.services.temperature_deviation.types import (
    DailyDeviationPoint,
    DailyDeviationSeriesQuery,
    StationDailySeries,
)


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


class TimescaleNationalIndicatorObservedDataSource(NationalIndicatorObservedDataSource):
    def fetch_daily_series(
        self,
        query: DailySeriesQuery,
    ) -> list[ObservedPoint]:
        qs = QuotidienneITN.objects.filter(
            date__gte=query.date_start,
            date__lte=query.date_end,
            station_code__in=ITN_STATION_CODES_FOR_QUERY,
        )

        if query.target_dates is not None:
            qs = qs.filter(date__in=query.target_dates)

        rows = qs.order_by("date", "station_code").values(
            "date", "station_code", "tntxm"
        )

        grouped: dict[dt.date, dict[str, float]] = defaultdict(dict)
        for row in rows:
            value = row["tntxm"]
            if value is None:
                continue
            grouped[row["date"]][row["station_code"]] = float(value)

        out: list[ObservedPoint] = []
        for day in sorted(grouped):
            itn = compute_itn_for_day(day, grouped[day])
            if itn is None:
                continue

            out.append(
                ObservedPoint(
                    date=day,
                    temperature=itn,
                )
            )

        return out


class TimescaleNationalIndicatorBaselineDataSource(NationalIndicatorBaselineDataSource):
    """
    Source baseline ITN basée sur les MV Timescale.
    """

    def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
        row = ITNBaselineDaily19912020.objects.get(
            month=day.month,
            day_of_month=day.day,
        )

        return self._map(row.itn_mean, row.itn_stddev)

    def fetch_monthly_baseline(self, month: int) -> BaselinePoint:
        row = ITNBaselineMonthly19912020.objects.get(month=month)
        return self._map(row.itn_mean, row.itn_stddev)

    def fetch_yearly_baseline(self) -> BaselinePoint:
        row = ITNBaselineYearly19912020.objects.first()
        if row is None:
            raise ValueError("Baseline yearly ITN introuvable")
        return self._map(row.itn_mean, row.itn_stddev)

    @staticmethod
    def _map(mean: float, std: float) -> BaselinePoint:
        return BaselinePoint(
            baseline_mean=float(mean),
            baseline_std_dev_upper=float(mean + std),
            baseline_std_dev_lower=float(mean - std),
            baseline_max=0.0,  # TODO MV future
            baseline_min=0.0,  # TODO MV future
        )


class TimescaleTemperatureDeviationDailyDataSource(TemperatureDeviationDailyDataSource):
    def _baseline_subquery(self):
        return BaselineStationDailyMean19912020.objects.filter(
            station_code=OuterRef("station_code"),
            month=OuterRef("month"),
            day=OuterRef("day"),
        ).values("baseline_mean_tntxm")[:1]

    def fetch_stations_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[StationDailySeries]:
        if not query.station_ids:
            return []

        baseline_sq = self._baseline_subquery()

        rows = (
            QuotidienneITN.objects.filter(
                date__gte=query.date_start,
                date__lte=query.date_end,
                station_code__in=query.station_ids,
            )
            .annotate(
                month=ExtractMonth("date"),
                day=ExtractDay("date"),
            )
            .annotate(
                baseline_mean=Subquery(baseline_sq),
            )
            .filter(baseline_mean__isnull=False)
            .order_by("station_code", "date")
            .values("station_code", "date", "tntxm", "baseline_mean")
        )

        # lookup station names (1 requête, pas de join lourd)
        station_names = {
            s.station_code: s.name
            for s in Station.objects.filter(station_code__in=query.station_ids).only(
                "station_code", "name"
            )
        }

        grouped: dict[str, list[DailyDeviationPoint]] = defaultdict(list)

        for row in rows:
            grouped[row["station_code"]].append(
                DailyDeviationPoint(
                    date=row["date"],
                    temperature=float(row["tntxm"]),
                    baseline_mean=float(row["baseline_mean"]),
                )
            )

        return [
            StationDailySeries(
                station_id=station_id,
                station_name=station_names.get(station_id, station_id),
                points=grouped[station_id],
            )
            for station_id in query.station_ids
            if station_id in grouped
        ]

    def fetch_national_daily_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[DailyDeviationPoint]:
        raise NotImplementedError(
            "National deviation is not implemented yet: waiting for ITN baseline."
        )
