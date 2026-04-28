import datetime as dt

import pytest
from django.db import connection

from weather.services.national_indicator.stations import (
    REIMS_COURCY,
    REIMS_PRUNAY,
    expected_station_codes,
)
from weather.tests.helpers.itn import insert_quotidienne


@pytest.mark.django_db
def test_itn_mv_returns_mean_when_all_stations_present():
    day = dt.date(2024, 1, 1)

    codes = list(expected_station_codes(day))

    values = []
    for i, code in enumerate(codes):
        temp = float(i)
        values.append(temp)
        insert_quotidienne(day, code, tx=temp, tn=temp)

    with connection.cursor() as cur:
        cur.execute("REFRESH MATERIALIZED VIEW mv_itn_daily_observed;")
        cur.execute(
            """
            SELECT temperature
            FROM mv_itn_daily_observed
            WHERE date = %s
        """,
            [day],
        )
        row = cur.fetchone()

    assert row is not None
    assert row[0] == pytest.approx(sum(values) / len(values))


@pytest.mark.django_db
def test_itn_mv_returns_no_row_if_two_stations_missing():
    day = dt.date(2024, 1, 1)

    codes = list(expected_station_codes(day))[:-2]  # 28 stations

    for code in codes:
        insert_quotidienne(day, code, tx=10.0, tn=10.0)

    with connection.cursor() as cur:
        cur.execute("REFRESH MATERIALIZED VIEW mv_itn_daily_observed;")
        cur.execute(
            """
            SELECT COUNT(*)
            FROM mv_itn_daily_observed
            WHERE date = %s
        """,
            [day],
        )
        count = cur.fetchone()[0]

    assert count == 0


@pytest.mark.django_db
def test_itn_mv_uses_correct_reims_station():
    day = dt.date(2024, 1, 1)

    expected_codes = expected_station_codes(day)

    for code in expected_codes:
        insert_quotidienne(day, code, tx=10.0, tn=10.0)

    wrong = REIMS_PRUNAY if REIMS_COURCY in expected_codes else REIMS_COURCY
    insert_quotidienne(day, wrong, tx=50.0, tn=50.0)

    with connection.cursor() as cur:
        cur.execute("REFRESH MATERIALIZED VIEW mv_itn_daily_observed;")
        cur.execute(
            """
            SELECT temperature
            FROM mv_itn_daily_observed
            WHERE date = %s
        """,
            [day],
        )
        value = cur.fetchone()[0]

    assert value == pytest.approx(10.0)


@pytest.mark.django_db
def test_itn_mv_returns_mean_when_one_station_missing():
    day = dt.date(2024, 1, 1)

    expected_codes = list(expected_station_codes(day))

    # on enlève 1 station → 29 restantes
    codes = expected_codes[:-1]

    values = []
    for i, code in enumerate(codes):
        temp = float(i)
        values.append(temp)
        insert_quotidienne(day, code, tx=temp, tn=temp)

    with connection.cursor() as cur:
        cur.execute("REFRESH MATERIALIZED VIEW public.mv_itn_daily_observed;")
        cur.execute(
            """
            SELECT temperature
            FROM mv_itn_daily_observed
            WHERE date = %s
        """,
            [day],
        )
        row = cur.fetchone()

    assert row is not None
    assert row[0] == pytest.approx(sum(values) / len(values))
