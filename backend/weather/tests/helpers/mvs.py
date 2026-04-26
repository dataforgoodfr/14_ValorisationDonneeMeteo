import datetime as dt

from django.db import connection


def set_cutoff(date: dt.date) -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_battus_meta;")
        cur.execute(
            "INSERT INTO public.mv_records_battus_meta (cutoff_date) VALUES (%s);",
            [date],
        )


def clear_mv_records_battus() -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_battus;")
        cur.execute("TRUNCATE public.mv_records_battus_meta;")


def insert_mv_record(
    station_code: str,
    station_name: str,
    period_type: str,
    period_value: str | None,
    record_type: str,
    value: float,
    date: dt.date,
    department: int = 75,
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_records_battus
                (period_type, period_value, record_type,
                 station_code, station_name, department,
                 record_value, record_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                period_type,
                period_value,
                record_type,
                station_code,
                station_name,
                department,
                value,
                date,
            ],
        )
