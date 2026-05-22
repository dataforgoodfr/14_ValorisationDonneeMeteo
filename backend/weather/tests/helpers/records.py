"""
Helpers d'insertion pour les pipelines de records :
- `mv_records_battus`              : table des records battus progressifs
  (recréée comme table régulière par le conftest).
- `mv_records_battus_meta`         : table de métadonnées contenant la
  `cutoff_date`.
- `mv_records_absolus_par_mois`    : table des records absolus mensuels
  (recréée comme table régulière par le conftest ; source de
  v_records_absolus_par_type pour le period_type=month).
"""

from __future__ import annotations

import datetime as dt

from django.db import connection


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
                (period_type,     period_value,     record_type,     station_code,     station_name,     department,     record_value,     record_date)
            VALUES
                (%(period_type)s, %(period_value)s, %(record_type)s, %(station_code)s, %(station_name)s, %(department)s, %(record_value)s, %(record_date)s)
            """,
            {
                "period_type": period_type,
                "period_value": period_value,
                "record_type": record_type,
                "station_code": station_code,
                "station_name": station_name,
                "department": department,
                "record_value": value,
                "record_date": date,
            },
        )


def set_cutoff(date: dt.date) -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_battus_meta;")
        cur.execute(
            """
            INSERT INTO public.mv_records_battus_meta (cutoff_date)
            VALUES (%(cutoff_date)s);
            """,
            {"cutoff_date": date},
        )


def clear_mv() -> None:
    with connection.cursor() as cur:
        cur.execute("TRUNCATE public.mv_records_battus;")
        cur.execute("TRUNCATE public.mv_records_battus_meta;")


def insert_mv_records_absolus_par_mois(
    *,
    station_code: str,
    month: int,
    txx_max: float | None = None,
    txx_max_date: dt.date | None = None,
    tnn_min: float | None = None,
    tnn_min_date: dt.date | None = None,
) -> None:
    """Insère le record absolu mensuel d'une station. Source de
    v_records_absolus_par_type (period_type='month')."""
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_records_absolus_par_mois
                (station_code,     month,     txx_max,     txx_max_date,     tnn_min,     tnn_min_date)
            VALUES
                (%(station_code)s, %(month)s, %(txx_max)s, %(txx_max_date)s, %(tnn_min)s, %(tnn_min_date)s)
            """,
            {
                "station_code": station_code,
                "month": month,
                "txx_max": txx_max,
                "txx_max_date": txx_max_date,
                "tnn_min": tnn_min,
                "tnn_min_date": tnn_min_date,
            },
        )
