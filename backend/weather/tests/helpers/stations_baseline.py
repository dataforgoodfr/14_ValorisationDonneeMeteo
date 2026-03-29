from django.db import connection


def insert_station_daily_baseline(
    station_code: str,
    month: int,
    day: int,
    mean: float,
    *,
    sample_count: int = 24,
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.baseline_station_daily_mean_1991_2020
                (station_code, month, day, sample_count, baseline_mean_tntxm)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [station_code, month, day, sample_count, mean],
        )
