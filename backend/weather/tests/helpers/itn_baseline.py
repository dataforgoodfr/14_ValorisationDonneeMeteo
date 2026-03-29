from django.db import connection


def insert_daily_baseline(
    month: int,
    day: int,
    mean: float,
    std: float,
    *,
    sample_size: int = 30,
    p20: float = 8.0,
    p80: float = 12.0,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_1991_2020
                (month, day_of_month, sample_size, itn_mean, itn_stddev, itn_p20, itn_p80)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            [month, day, sample_size, mean, std, p20, p80],
        )


def insert_monthly_baseline(
    month: int,
    mean: float,
    std: float,
    *,
    sample_size: int = 30,
    p20: float = 18.0,
    p80: float = 22.0,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_monthly_1991_2020
                (month, sample_size, itn_mean, itn_stddev, itn_p20, itn_p80)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            [month, sample_size, mean, std, p20, p80],
        )


def insert_yearly_baseline(
    sample_size: int,
    mean: float,
    std: float,
    *,
    p20: float = 28.0,
    p80: float = 32.0,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO mv_itn_baseline_yearly_1991_2020
                (sample_size, itn_mean, itn_stddev, itn_p20, itn_p80)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [sample_size, mean, std, p20, p80],
        )
