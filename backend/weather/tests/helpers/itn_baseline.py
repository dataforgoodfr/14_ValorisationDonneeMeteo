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
            INSERT INTO v_itn_baseline_daily_1991_2020
                   (month,     day_of_month,     sample_size,     itn_mean,     itn_stddev,     itn_p20,     itn_p80)
            VALUES (%(month)s, %(day_of_month)s, %(sample_size)s, %(itn_mean)s, %(itn_stddev)s, %(itn_p20)s, %(itn_p80)s)
            """,
            {
                "month": month,
                "day_of_month": day,
                "sample_size": sample_size,
                "itn_mean": mean,
                "itn_stddev": std,
                "itn_p20": p20,
                "itn_p80": p80,
            },
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
            INSERT INTO v_itn_baseline_monthly_1991_2020
                   (month,     sample_size,     itn_mean,     itn_stddev,     itn_p20,     itn_p80)
            VALUES (%(month)s, %(sample_size)s, %(itn_mean)s, %(itn_stddev)s, %(itn_p20)s, %(itn_p80)s)
            """,
            {
                "month": month,
                "sample_size": sample_size,
                "itn_mean": mean,
                "itn_stddev": std,
                "itn_p20": p20,
                "itn_p80": p80,
            },
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
            INSERT INTO v_itn_baseline_yearly_1991_2020
                   (sample_size,     itn_mean,     itn_stddev,     itn_p20,     itn_p80)
            VALUES (%(sample_size)s, %(itn_mean)s, %(itn_stddev)s, %(itn_p20)s, %(itn_p80)s)
            """,
            {
                "sample_size": sample_size,
                "itn_mean": mean,
                "itn_stddev": std,
                "itn_p20": p20,
                "itn_p80": p80,
            },
        )
