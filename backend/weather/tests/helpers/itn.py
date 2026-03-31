import datetime as dt

from django.db import connection

from weather.services.national_indicator.stations import expected_station_codes
from weather.tests.helpers.stations import insert_station


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
