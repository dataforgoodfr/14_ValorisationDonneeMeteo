import datetime as dt

from django.db import connection

from weather.services.national_indicator.stations import expected_station_codes
from weather.tests.helpers.stations import insert_station

# Reproduit la logique de 006 + 007 : daily ITN depuis v_quotidienne_itn,
# avec 29 fév synthétique pour les années non-bissextiles.
# Les CTEs monthly_itn et yearly_itn filtrent les jours fictifs (WHERE NOT is_fictive)
# pour rester cohérents avec le calcul de la température observée dans le service.
_ITN_ALL_DAYS_CTE = """
    WITH source AS (
        SELECT q.station_code, q.date AS day, q.tntxm
        FROM v_quotidienne_itn q
        WHERE q.station_code IN (
            '47091001','20148001','25056001','33281001','73054001',
            '29075001','14137001','36063001','63113001','16089001',
            '21473001','72181001','59343001','69029001','13054001',
            '26198001','54526001','44020001','58160001','06088001',
            '30189001','45055001','75114001','64549001','66136001',
            '86027001','35281001','67124001','31069001',
            '51183001','51449002'
        )
    ),
    normalized AS (
        SELECT *
        FROM source
        WHERE NOT (
            station_code = CASE
                WHEN day < DATE '2012-05-08' THEN '51449002'
                ELSE '51183001'
            END
        )
    ),
    daily_itn AS (
        SELECT
            n.day                          AS date,
            EXTRACT(YEAR  FROM n.day)::int AS year,
            EXTRACT(MONTH FROM n.day)::int AS month,
            EXTRACT(DAY   FROM n.day)::int AS day_of_month,
            FALSE                          AS is_fictive,
            AVG(n.tntxm)                   AS itn
        FROM normalized n
        GROUP BY n.day
        HAVING COUNT(DISTINCT n.station_code) >= 29
    ),
    feb29_fictive AS (
        SELECT
            NULL::date AS date,
            feb28.year,
            2          AS month,
            29         AS day_of_month,
            TRUE       AS is_fictive,
            (feb28.itn + mar01.itn) / 2.0 AS itn
        FROM daily_itn feb28
        INNER JOIN daily_itn mar01
            ON  mar01.year         = feb28.year
            AND mar01.month        = 3
            AND mar01.day_of_month = 1
        WHERE feb28.month        = 2
          AND feb28.day_of_month = 28
          AND NOT (
              (feb28.year % 4 = 0 AND feb28.year % 100 <> 0)
              OR (feb28.year % 400 = 0)
          )
    ),
    all_days AS (
        SELECT * FROM daily_itn
        UNION ALL
        SELECT * FROM feb29_fictive
    )
"""


def seed_absolute_extremes_from_quotidienne() -> None:
    """
    Calcule et insère les extremes absolus depuis v_quotidienne_itn.
    Équivalent du seed script shell, utilisable dans les tests d'intégration.
    Les jours fictifs (29 fév synthétique) sont exclus des agrégations
    mensuelles et annuelles.
    """
    with connection.cursor() as cur:
        cur.execute(
            _ITN_ALL_DAYS_CTE
            + """
            INSERT INTO public.mv_itn_absolute_extremes_daily
                (month, day_of_month, absolute_min, absolute_max)
            SELECT month, day_of_month, MIN(itn), MAX(itn)
            FROM all_days
            GROUP BY month, day_of_month
            ON CONFLICT (month, day_of_month) DO UPDATE SET
                absolute_min = EXCLUDED.absolute_min,
                absolute_max = EXCLUDED.absolute_max
            """
        )
        cur.execute(
            _ITN_ALL_DAYS_CTE
            + """
            , monthly_itn AS (
                SELECT year, month, AVG(itn) AS monthly_mean
                FROM all_days
                WHERE NOT is_fictive
                GROUP BY year, month
            )
            INSERT INTO public.mv_itn_absolute_extremes_monthly
                (month, absolute_min, absolute_max)
            SELECT month, MIN(monthly_mean), MAX(monthly_mean)
            FROM monthly_itn
            GROUP BY month
            ON CONFLICT (month) DO UPDATE SET
                absolute_min = EXCLUDED.absolute_min,
                absolute_max = EXCLUDED.absolute_max
            """
        )
        cur.execute("DELETE FROM public.mv_itn_absolute_extremes_yearly")
        cur.execute(
            _ITN_ALL_DAYS_CTE
            + """
            , yearly_itn AS (
                SELECT year, AVG(itn) AS yearly_mean
                FROM all_days
                WHERE NOT is_fictive
                GROUP BY year
            )
            INSERT INTO public.mv_itn_absolute_extremes_yearly
                (absolute_min, absolute_max)
            SELECT MIN(yearly_mean), MAX(yearly_mean)
            FROM yearly_itn
            """
        )


def insert_quotidienne(day: dt.date, code: str, tntxm: float) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Quotidienne"
                ("NUM_POSTE","NOM_USUEL","LAT","LON","ALTI","AAAAMMJJ","TNTXM")
            VALUES
                (%(code)s, %(name)s, 0, 0, 0, %(day)s, %(tntxm)s)
            ON CONFLICT ("NUM_POSTE","AAAAMMJJ")
            DO UPDATE SET "TNTXM" = EXCLUDED."TNTXM"
            """,
            {
                "code": code,
                "name": f"ST {code}",
                "day": day,
                "tntxm": tntxm,
            },
        )


def insert_complete_itn_day(day: dt.date, value: float):
    for code in expected_station_codes(day):
        insert_station(code)
        insert_quotidienne(day, code, value)


def insert_itn_day_values(day: dt.date, value: float) -> None:
    """Insère une valeur ITN pour tous les codes de stations d'un jour,
    sans insérer les stations. Suffisant pour alimenter v_quotidienne_itn
    car cette vue ne joint pas la table Station."""
    for code in expected_station_codes(day):
        insert_quotidienne(day, code, value)


def insert_absolute_extremes_daily(
    month: int, day_of_month: int, absolute_min: float, absolute_max: float
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_itn_absolute_extremes_daily
                (month, day_of_month, absolute_min, absolute_max)
            VALUES
                (%(month)s, %(day_of_month)s, %(absolute_min)s, %(absolute_max)s)
            ON CONFLICT (month, day_of_month)
            DO UPDATE SET
                absolute_min = EXCLUDED.absolute_min,
                absolute_max = EXCLUDED.absolute_max
            """,
            {
                "month": month,
                "day_of_month": day_of_month,
                "absolute_min": absolute_min,
                "absolute_max": absolute_max,
            },
        )


def insert_absolute_extremes_monthly(
    month: int, absolute_min: float, absolute_max: float
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_itn_absolute_extremes_monthly
                (month, absolute_min, absolute_max)
            VALUES
                (%(month)s, %(absolute_min)s, %(absolute_max)s)
            ON CONFLICT (month)
            DO UPDATE SET
                absolute_min = EXCLUDED.absolute_min,
                absolute_max = EXCLUDED.absolute_max
            """,
            {
                "month": month,
                "absolute_min": absolute_min,
                "absolute_max": absolute_max,
            },
        )


def insert_absolute_extremes_yearly(absolute_min: float, absolute_max: float) -> None:
    with connection.cursor() as cur:
        cur.execute("DELETE FROM public.mv_itn_absolute_extremes_yearly;")
        cur.execute(
            """
            INSERT INTO public.mv_itn_absolute_extremes_yearly
                (absolute_min, absolute_max)
            VALUES
                (%(absolute_min)s, %(absolute_max)s)
            """,
            {"absolute_min": absolute_min, "absolute_max": absolute_max},
        )
