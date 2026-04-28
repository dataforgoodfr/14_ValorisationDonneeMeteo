import datetime as dt

from django.db import connection

from weather.services.national_indicator.stations import expected_station_codes
from weather.tests.helpers.quotidienne import insert_quotidienne


def insert_complete_itn_day(day: dt.date, value: float):
    for code in expected_station_codes(day):
        insert_quotidienne(day, code, value)


def insert_itn_daily_observed(
    day: dt.date,
    temperature: float,
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_itn_daily_observed
                (date, year, month, day_of_month, temperature)
            VALUES
                (%(date)s, %(year)s, %(month)s, %(day_of_month)s, %(temperature)s)
            ON CONFLICT (date)
            DO UPDATE SET
                temperature = EXCLUDED.temperature
            """,
            {
                "date": day,
                "year": day.year,
                "month": day.month,
                "day_of_month": day.day,
                "temperature": temperature,
            },
        )


def clear_itn_daily_observed() -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_itn_daily_observed;")
