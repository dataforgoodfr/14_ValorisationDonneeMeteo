import datetime as dt
import pathlib

from django.db import connection

from weather.services.national_indicator.stations import expected_station_codes
from weather.tests.helpers.stations import insert_station

_MV_ITN_DIR = (
    pathlib.Path(__file__).resolve().parents[3] / "sql" / "materialized_views" / "itn"
)


def insert_itn_daily(
    year: int,
    month: int,
    day_of_month: int,
    itn: float,
) -> None:
    """Insère une ligne dans mv_itn_daily_all_years.

    Reproduit l'invariant de mv_itn_daily_all_years (006) : les données
    antérieures au 1er janvier 1947 sont ignorées.
    """
    if year < 1947:
        return
    date = dt.date(year, month, day_of_month)
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_itn_daily_all_years
                   (date,     year,     month,     day_of_month,     itn)
            VALUES (%(date)s, %(year)s, %(month)s, %(day_of_month)s, %(itn)s)
            """,
            {
                "date": date,
                "year": year,
                "month": month,
                "day_of_month": day_of_month,
                "itn": itn,
            },
        )


def insert_quotidienne(day: dt.date, code: str, tntxm: float) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public."Quotidienne"
                ("NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMMJJ", "TNTXM")
            VALUES
                (%(code)s,    %(name)s,    0,     0,     0,      %(day)s,    %(tntxm)s)
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
