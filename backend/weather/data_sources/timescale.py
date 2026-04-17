from __future__ import annotations

import datetime as dt
from collections import defaultdict

from django.db import connection
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
)
from weather.services.national_indicator.types import (
    ObservedPoint as NationalObservedPoint,
)
from weather.services.records.types import (
    RecordsQuery,
    StationRecords,
    TemperatureRecord,
)
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
from weather.services.temperature_records.types import (
    SEASON_MONTHS,
    TemperatureRecordEntry,
    TemperatureRecordsRequest,
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


def _station_daily_baseline_subquery():
    return BaselineStationDailyMean19912020.objects.filter(
        station_code=OuterRef("station_code"),
        month=OuterRef("month"),
        day=OuterRef("day"),
    ).values("baseline_mean_tntxm")[:1]


def _station_name_subquery():
    return Station.objects.filter(station_code=OuterRef("station_code")).values("name")[
        :1
    ]


def _daily_station_queryset(
    date_start: dt.date,
    date_end: dt.date,
):
    baseline_sq = _station_daily_baseline_subquery()

    return (
        QuotidienneITN.objects.filter(
            date__gte=date_start,
            date__lte=date_end,
        )
        .annotate(
            month=ExtractMonth("date"),
            day=ExtractDay("date"),
        )
        .annotate(
            baseline_mean_day=Subquery(baseline_sq),
        )
        .filter(baseline_mean_day__isnull=False)
    )


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


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
    ) -> list[NationalObservedPoint]:
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

        out: list[NationalObservedPoint] = []
        for day in sorted(grouped):
            itn = compute_itn_for_day(day, grouped[day])
            if itn is None:
                continue

            out.append(
                NationalObservedPoint(
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


class TimescaleTemperatureDeviationDailyDataSource(
    TemperatureDeviationDailyDataSource,
    TemperatureDeviationOverviewDataSource,
):
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

    def fetch_national_observed_series(
        self, query: DailyDeviationSeriesQuery
    ) -> list[ObservedPoint]:
        observed_points = (
            TimescaleNationalIndicatorObservedDataSource().fetch_daily_series(
                DailySeriesQuery(
                    date_start=query.date_start,
                    date_end=query.date_end,
                    target_dates=None,
                )
            )
        )

        return [
            ObservedPoint(
                date=point.date,
                temperature=float(point.temperature),
            )
            for point in observed_points
        ]

    def fetch_national_daily_baseline(self) -> list[DailyBaselinePoint]:
        rows = ITNBaselineDaily19912020.objects.all().order_by("month", "day_of_month")

        return [
            DailyBaselinePoint(
                month=row.month,
                day_of_month=row.day_of_month,
                mean=float(row.itn_mean),
            )
            for row in rows
        ]

    def fetch_national_monthly_baseline(self) -> list[MonthlyBaselinePoint]:
        rows = ITNBaselineMonthly19912020.objects.all().order_by("month")

        return [
            MonthlyBaselinePoint(
                month=row.month,
                mean=float(row.itn_mean),
            )
            for row in rows
        ]

    def fetch_national_yearly_baseline(self) -> YearlyBaselinePoint | None:
        row = ITNBaselineYearly19912020.objects.first()
        if row is None:
            return None

        return YearlyBaselinePoint(mean=float(row.itn_mean))

    def fetch_national_mean_deviation(
        self,
        *,
        date_start: dt.date,
        date_end: dt.date,
    ) -> float:
        observed_points = (
            TimescaleNationalIndicatorObservedDataSource().fetch_daily_series(
                DailySeriesQuery(
                    date_start=date_start,
                    date_end=date_end,
                    target_dates=None,
                )
            )
        )

        if not observed_points:
            return 0.0

        baseline_by_day = {
            (row.month, row.day_of_month): float(row.itn_mean)
            for row in ITNBaselineDaily19912020.objects.all()
        }

        deviations = []
        for point in observed_points:
            baseline_mean = baseline_by_day.get((point.date.month, point.date.day))
            if baseline_mean is None:
                continue
            deviations.append(float(point.temperature) - baseline_mean)

        if not deviations:
            return 0.0

        return _mean(deviations)

    def fetch_station_overview(
        self,
        query: TemperatureDeviationOverviewQuery,
    ) -> TemperatureDeviationOverviewResult:
        ordering_map = {
            "station_name": "station_name ASC, station_id ASC",
            "-station_name": "station_name DESC, station_id ASC",
            "temperature_mean": "temperature_mean ASC, station_id ASC",
            "-temperature_mean": "temperature_mean DESC, station_id ASC",
            "deviation": "deviation ASC, station_id ASC",
            "-deviation": "deviation DESC, station_id ASC",
            "department": "department ASC NULLS LAST, station_id ASC",
            "-department": "department DESC NULLS LAST, station_id ASC",
            "region": "region ASC NULLS LAST, station_id ASC",
            "-region": "region DESC NULLS LAST, station_id ASC",
        }

        order_sql = ordering_map[query.ordering]

        where_clauses = []
        params: list = [query.date_start, query.date_end]

        if query.station_search:
            where_clauses.append("station_name ILIKE %s")
            params.append(f"%{query.station_search}%")

        if query.station_ids:
            where_clauses.append("station_id = ANY(%s)")
            params.append(list(query.station_ids))

        if query.temperature_mean_min is not None:
            where_clauses.append("temperature_mean >= %s")
            params.append(query.temperature_mean_min)

        if query.temperature_mean_max is not None:
            where_clauses.append("temperature_mean <= %s")
            params.append(query.temperature_mean_max)

        if query.deviation_min is not None:
            where_clauses.append("deviation >= %s")
            params.append(query.deviation_min)

        if query.deviation_max is not None:
            where_clauses.append("deviation <= %s")
            params.append(query.deviation_max)

        if query.alt_min is not None:
            where_clauses.append("alt >= %s")
            params.append(query.alt_min)

        if query.alt_max is not None:
            where_clauses.append("alt <= %s")
            params.append(query.alt_max)

        if query.departments:
            where_clauses.append("department = ANY(%s)")
            params.append(list(query.departments))

        if query.regions:
            where_clauses.append("region = ANY(%s)")
            params.append(list(query.regions))

        filtered_where_sql = ""
        if where_clauses:
            filtered_where_sql = "WHERE " + " AND ".join(where_clauses)

        base_cte = """
            WITH station_agg AS (
                SELECT
                    q.station_code AS station_id,
                    AVG(q.tntxm)::double precision AS temperature_mean,
                    AVG(b.baseline_mean_tntxm)::double precision AS baseline_mean
                FROM v_quotidienne_itn q
                    JOIN baseline_station_daily_mean_1991_2020 b
                        ON b.station_code = q.station_code
                            AND b.month = EXTRACT(MONTH FROM q.date)::int
                            AND b.day = EXTRACT(DAY FROM q.date)::int
                WHERE %s <= q.date AND q.date <= %s
                GROUP BY q.station_code
            ),
            station_enriched AS (
                SELECT
                    a.station_id,
                    COALESCE(s.name, a.station_id) AS station_name,
                    s.lat AS lat,
                    s.lon AS lon,
                    s.departement AS department,
                    s.alt AS alt,
                    COALESCE(r.region, 'Autre') AS region,
                    a.temperature_mean,
                    a.baseline_mean,
                    (a.temperature_mean - a.baseline_mean) AS deviation
                FROM station_agg a
                    LEFT JOIN v_station s
                        ON s.station_code = a.station_id
                    LEFT JOIN ref_department_region r
                        ON r.departement = s.departement
            )
        """

        count_sql = (
            base_cte
            + f"""
            SELECT COUNT(*)
            FROM station_enriched
            {filtered_where_sql}
            """
        )

        page_params = [*params, query.limit, query.offset]

        page_sql = (
            base_cte
            + f"""
            SELECT
                station_id,
                station_name,
                lat,
                lon,
                department,
                alt,
                region,
                temperature_mean,
                baseline_mean,
                deviation
            FROM station_enriched
            {filtered_where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
            """
        )

        with connection.cursor() as cur:
            cur.execute(count_sql, params)
            total_count = cur.fetchone()[0]

            cur.execute(page_sql, page_params)
            columns = [col[0] for col in cur.description]
            rows = [dict(zip(columns, row, strict=False)) for row in cur.fetchall()]

        stations = [
            TemperatureDeviationOverviewStation(
                station_id=row["station_id"],
                station_name=row["station_name"],
                lat=row["lat"],
                lon=row["lon"],
                department=str(row["department"])
                if row["department"] is not None
                else None,
                alt=row["alt"],
                region=row["region"],
                temperature_mean=float(row["temperature_mean"]),
                baseline_mean=float(row["baseline_mean"]),
                deviation=float(row["deviation"]),
            )
            for row in rows
        ]

        return TemperatureDeviationOverviewResult(
            national_deviation_mean=0.0,  # ignoré par le service
            pagination=Pagination(
                total_count=total_count,
                limit=query.limit,
                offset=query.offset,
            ),
            stations=stations,
        )


class TimescaleTemperatureRecordsDataSource:
    """
    Data source réelle : calcule les records progressifs via window function SQL.
    Retourne N lignes par station (une par fois que la station a battu son propre record).
    """

    def fetch_records(
        self, request: TemperatureRecordsRequest
    ) -> list[TemperatureRecordEntry]:
        col = "TX" if request.type_records == "hot" else "TN"
        agg = "MAX" if request.type_records == "hot" else "MIN"
        cmp = ">" if request.type_records == "hot" else "<"

        period_clause, params = self._period_clause(request)

        sql = f"""
            WITH ordered AS (
                SELECT
                    q."NUM_POSTE",
                    q."AAAAMMJJ",
                    q."{col}",
                    {agg}(q."{col}") OVER (
                        PARTITION BY q."NUM_POSTE"
                        ORDER BY q."AAAAMMJJ"
                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                    ) AS prev_val
                FROM public."Quotidienne" q
                WHERE {period_clause}
                  AND q."{col}" IS NOT NULL
            )
            SELECT
                o."NUM_POSTE",
                s.name,
                s.departement,
                o."{col}",
                o."AAAAMMJJ"
            FROM ordered o
            JOIN public.v_station s ON s.station_code = o."NUM_POSTE"
            WHERE o.prev_val IS NULL OR o."{col}" {cmp} o.prev_val
            ORDER BY s.name, o."AAAAMMJJ"
        """

        with connection.cursor() as cur:
            cur.execute(sql, params)
            cols = [c.name for c in cur.description]
            rows = [dict(zip(cols, row, strict=False)) for row in cur.fetchall()]

        return [
            TemperatureRecordEntry(
                station_id=row["NUM_POSTE"].strip(),
                station_name=row["name"],
                department=str(row["departement"])
                if row["departement"] is not None
                else "",
                record_value=float(row[col]),
                record_date=row["AAAAMMJJ"].date()
                if isinstance(row["AAAAMMJJ"], dt.datetime)
                else row["AAAAMMJJ"],
            )
            for row in rows
        ]

    def _period_clause(self, request: TemperatureRecordsRequest) -> tuple[str, list]:
        return _temperature_records_period_clause(request)


def _temperature_records_period_clause(
    request: TemperatureRecordsRequest,
) -> tuple[str, list]:
    if request.period_type == "month":
        return 'EXTRACT(MONTH FROM q."AAAAMMJJ") = %s', [request.month]
    elif request.period_type == "season":
        months = list(SEASON_MONTHS[request.season])
        placeholders = ", ".join(["%s"] * len(months))
        return f'EXTRACT(MONTH FROM q."AAAAMMJJ") IN ({placeholders})', months
    else:
        return "TRUE", []


def _temperature_records_period_clause_named(
    request: TemperatureRecordsRequest,
) -> tuple[str, dict]:
    """Variante de _temperature_records_period_clause avec placeholders nommés %(…)s."""
    if request.period_type == "month":
        return 'EXTRACT(MONTH FROM q."AAAAMMJJ") = %(period_month)s', {
            "period_month": request.month
        }
    elif request.period_type == "season":
        months = list(SEASON_MONTHS[request.season])
        named = {f"period_season_{i}": m for i, m in enumerate(months)}
        placeholders = ", ".join(f"%(period_season_{i})s" for i in range(len(months)))
        return f'EXTRACT(MONTH FROM q."AAAAMMJJ") IN ({placeholders})', named
    else:
        return "TRUE", {}


class MaterializedTemperatureRecordsDataSource:
    """
    Data source optimisée : lit les records pré-calculés depuis la vue
    matérialisée mv_records_battus. Temps de réponse < 10 ms.

    Pré-requis : la MV doit exister en base. La créer avec :
        psql < backend/sql/materialized_views/records/001_mv_records_battus.sql

    Rafraîchissement après import de nouvelles données :
        python manage.py refresh_records_mv
    """

    def fetch_records(
        self, request: TemperatureRecordsRequest
    ) -> list[TemperatureRecordEntry]:
        record_type = "TX" if request.type_records == "hot" else "TN"

        if request.period_type == "month":
            period_value: str | None = str(request.month)
        elif request.period_type == "season":
            period_value = request.season
        else:
            period_value = None

        sql = """
            SELECT station_code, station_name, department, record_value, record_date
            FROM public.mv_records_battus
            WHERE record_type = %s
              AND period_type = %s
              AND period_value IS NOT DISTINCT FROM %s
            ORDER BY station_name, record_date
        """

        with connection.cursor() as cur:
            cur.execute(sql, [record_type, request.period_type, period_value])
            cols = [c.name for c in cur.description]
            rows = [dict(zip(cols, row, strict=False)) for row in cur.fetchall()]

        return [
            TemperatureRecordEntry(
                station_id=row["station_code"].strip(),
                station_name=row["station_name"],
                department=str(row["department"])
                if row["department"] is not None
                else "",
                record_value=float(row["record_value"]),
                record_date=row["record_date"].date()
                if isinstance(row["record_date"], dt.datetime)
                else row["record_date"],
            )
            for row in rows
        ]


class HybridTemperatureRecordsDataSource:
    """
    Data source hybride : lit les records pré-calculés depuis mv_records_battus
    (snapshot figé) et complète à chaud les nouvelles données (après cutoff_date)
    via une window function amorcée par les records actuels de la MV.

    La MV n'est jamais rafraîchie. La cutoff_date est stockée dans
    mv_records_battus_meta au moment de la création de la MV.

    Fallback silencieux vers la MV seule si mv_records_battus_meta est absente
    ou vide (env de dev sans script de seed exécuté).
    """

    def __init__(self) -> None:
        self._mv_source = MaterializedTemperatureRecordsDataSource()

    def fetch_records(
        self, request: TemperatureRecordsRequest
    ) -> list[TemperatureRecordEntry]:
        mv_results = self._mv_source.fetch_records(request)
        try:
            cutoff = self._get_cutoff_date()
        except Exception:
            return mv_results
        if cutoff is None:
            return mv_results
        hot_results = self._fetch_records_after_cutoff(request, cutoff)
        return mv_results + hot_results

    def _get_cutoff_date(self) -> dt.date | None:
        with connection.cursor() as cur:
            cur.execute("SELECT cutoff_date FROM public.mv_records_battus_meta LIMIT 1")
            row = cur.fetchone()
        return row[0] if row else None

    def _fetch_records_after_cutoff(
        self, request: TemperatureRecordsRequest, cutoff_date: dt.date
    ) -> list[TemperatureRecordEntry]:
        hot = request.type_records == "hot"
        col = "TX" if hot else "TN"
        agg = "MAX" if hot else "MIN"
        cmp = ">" if hot else "<"
        extremum_fn = "GREATEST" if hot else "LEAST"
        neutral_val = (
            "'-Infinity'::double precision" if hot else "'Infinity'::double precision"
        )
        record_type = col

        if request.period_type == "month":
            period_value: str | None = str(request.month)
        elif request.period_type == "season":
            period_value = request.season
        else:
            period_value = None

        period_clause, period_named_params = _temperature_records_period_clause_named(
            request
        )

        sql = f"""
            WITH mv_seeds AS (
                SELECT station_code, {agg}(record_value) AS seed_val
                FROM public.mv_records_battus
                WHERE record_type = %(record_type)s
                  AND period_type = %(period_type)s
                  AND period_value IS NOT DISTINCT FROM %(period_value)s
                GROUP BY station_code
            ),
            ordered AS (
                SELECT
                    q."NUM_POSTE",
                    q."AAAAMMJJ",
                    q."{col}",
                    {extremum_fn}(
                        COALESCE(s.seed_val, {neutral_val}),
                        COALESCE(
                            {agg}(q."{col}") OVER (
                                PARTITION BY q."NUM_POSTE"
                                ORDER BY q."AAAAMMJJ"
                                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                            ),
                            {neutral_val}
                        )
                    ) AS prev_val
                FROM public."Quotidienne" q
                LEFT JOIN mv_seeds s ON s.station_code = q."NUM_POSTE"
                WHERE q."AAAAMMJJ" > %(cutoff_date)s
                  AND {period_clause}
                  AND q."{col}" IS NOT NULL
            )
            SELECT
                o."NUM_POSTE",
                vs.name,
                vs.departement,
                o."{col}",
                o."AAAAMMJJ"
            FROM ordered o
            JOIN public.v_station vs ON vs.station_code = o."NUM_POSTE"
            WHERE o."{col}" {cmp} o.prev_val
            ORDER BY vs.name, o."AAAAMMJJ"
        """

        params = {
            "record_type": record_type,
            "period_type": request.period_type,
            "period_value": period_value,
            "cutoff_date": cutoff_date,
            **period_named_params,
        }

        with connection.cursor() as cur:
            cur.execute(sql, params)
            cols = [c.name for c in cur.description]
            rows = [dict(zip(cols, row, strict=False)) for row in cur.fetchall()]

        return [
            TemperatureRecordEntry(
                station_id=row["NUM_POSTE"].strip(),
                station_name=row["name"],
                department=str(row["departement"])
                if row["departement"] is not None
                else "",
                record_value=float(row[col]),
                record_date=row["AAAAMMJJ"].date()
                if isinstance(row["AAAAMMJJ"], dt.datetime)
                else row["AAAAMMJJ"],
            )
            for row in rows
        ]


class TimescaleRecordsDataSource:
    """
    Adaptateur qui implémente RecordsDataSource (nouvelle spec) en s'appuyant sur
    HybridTemperatureRecordsDataSource.

    Mapping :
      record_scope  → period_type  (all_time, monthly→month, seasonal→season)
      record_kind   → "absolute" = dernier record par station, "historical" = tous
      type_records  → "all" déclenche les deux passages hot + cold
    """

    _SCOPE_TO_PERIOD = {
        "all_time": "all_time",
        "monthly": "month",
        "seasonal": "season",
    }

    def __init__(self) -> None:
        self._hybrid = HybridTemperatureRecordsDataSource()

    def fetch_records(self, query: RecordsQuery) -> tuple[StationRecords, ...]:
        period_type = self._SCOPE_TO_PERIOD[query.record_scope]

        types: list[str] = (
            ["hot", "cold"] if query.type_records == "all" else [query.type_records]
        )

        hot_entries: list[TemperatureRecordEntry] = []
        cold_entries: list[TemperatureRecordEntry] = []

        for type_records in types:
            req = TemperatureRecordsRequest(
                period_type=period_type,
                type_records=type_records,
                month=query.month,
                season=query.season,
            )
            entries = self._hybrid.fetch_records(req)
            if type_records == "hot":
                hot_entries = entries
            else:
                cold_entries = entries

        station_hot: dict[str, list[TemperatureRecordEntry]] = defaultdict(list)
        station_cold: dict[str, list[TemperatureRecordEntry]] = defaultdict(list)
        station_name: dict[str, str] = {}
        station_department: dict[str, str] = {}

        for e in hot_entries:
            station_hot[e.station_id].append(e)
            station_name[e.station_id] = e.station_name
            station_department[e.station_id] = e.department

        for e in cold_entries:
            station_cold[e.station_id].append(e)
            station_name[e.station_id] = e.station_name
            station_department[e.station_id] = e.department

        all_ids: set[str] = set(station_hot) | set(station_cold)

        if query.station_ids:
            all_ids &= set(query.station_ids)

        if query.departments:
            all_ids = {
                sid
                for sid in all_ids
                if station_department.get(sid, _department_of_station(sid))
                in query.departments
            }

        result: list[StationRecords] = []
        for station_id in sorted(all_ids):
            hot_recs = station_hot.get(station_id, [])
            cold_recs = station_cold.get(station_id, [])

            if query.record_kind == "absolute":
                hot_recs = hot_recs[-1:] if hot_recs else []
                cold_recs = cold_recs[-1:] if cold_recs else []

            hot_recs = _apply_temperature_filter(
                hot_recs, query.temperature_min, query.temperature_max
            )
            cold_recs = _apply_temperature_filter(
                cold_recs, query.temperature_min, query.temperature_max
            )

            if not hot_recs and not cold_recs:
                continue

            result.append(
                StationRecords(
                    id=station_id,
                    name=station_name.get(station_id, station_id),
                    hot_records=tuple(
                        TemperatureRecord(value=e.record_value, date=e.record_date)
                        for e in hot_recs
                    ),
                    cold_records=tuple(
                        TemperatureRecord(value=e.record_value, date=e.record_date)
                        for e in cold_recs
                    ),
                )
            )

        return tuple(result)


def _department_of_station(station_id: str) -> str:
    if station_id.startswith(("971", "972", "973", "974", "976")):
        return station_id[:3]
    return station_id[:2]


def _apply_temperature_filter(
    entries: list[TemperatureRecordEntry],
    temperature_min: float | None,
    temperature_max: float | None,
) -> list[TemperatureRecordEntry]:
    return [
        e
        for e in entries
        if (temperature_min is None or e.record_value >= temperature_min)
        and (temperature_max is None or e.record_value <= temperature_max)
    ]
