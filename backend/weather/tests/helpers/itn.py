import datetime as dt
import pathlib

from django.db import connection

from weather.services.national_indicator.stations import expected_station_codes
from weather.tests.helpers.stations import insert_station

_MV_ITN_DIR = (
    pathlib.Path(__file__).resolve().parents[3] / "sql" / "materialized_views" / "itn"
)


def _mv_select(filename: str, mv_name: str) -> str:
    """Extrait le corps SELECT d'un fichier CREATE MATERIALIZED VIEW."""
    sql = (_MV_ITN_DIR / filename).read_text()
    after_as = sql.split(f"CREATE MATERIALIZED VIEW {mv_name} AS\n", 1)[1]
    return after_as.split(";")[0].strip()


def insert_itn_daily_with_feb29(
    year: int, month: int, day_of_month: int, itn: float, *, is_fictive: bool = False
) -> None:
    """Insère une ligne dans mv_itn_daily_all_years_with_feb29."""
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_itn_daily_all_years_with_feb29
                (year, month, day_of_month, is_fictive, itn)
            VALUES (%(year)s, %(month)s, %(day_of_month)s, %(is_fictive)s, %(itn)s)
            """,
            {
                "year": year,
                "month": month,
                "day_of_month": day_of_month,
                "is_fictive": is_fictive,
                "itn": itn,
            },
        )


def refresh_absolute_extremes_mvs() -> None:
    """
    Peuple les tables de test mv_itn_absolute_extremes_* en exécutant
    le SELECT exact des fichiers MV de production 008, 009 et 010.
    """
    daily_select = _mv_select(
        "008_mv_itn_absolute_extremes_daily.sql", "mv_itn_absolute_extremes_daily"
    )
    monthly_select = _mv_select(
        "009_mv_itn_absolute_extremes_monthly.sql", "mv_itn_absolute_extremes_monthly"
    )
    yearly_select = _mv_select(
        "010_mv_itn_absolute_extremes_yearly.sql", "mv_itn_absolute_extremes_yearly"
    )

    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_itn_absolute_extremes_daily")
        cur.execute(f"INSERT INTO public.mv_itn_absolute_extremes_daily {daily_select}")

        cur.execute("TRUNCATE public.mv_itn_absolute_extremes_monthly")
        cur.execute(
            f"INSERT INTO public.mv_itn_absolute_extremes_monthly {monthly_select}"
        )

        cur.execute("TRUNCATE public.mv_itn_absolute_extremes_yearly")
        cur.execute(
            f"INSERT INTO public.mv_itn_absolute_extremes_yearly {yearly_select}"
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
