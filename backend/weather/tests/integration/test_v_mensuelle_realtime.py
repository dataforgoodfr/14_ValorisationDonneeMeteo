"""
Tests d'intégration de la vue SQL `v_mensuelle_realtime`.

Agrège les valeurs journalières de `v_quotidienne` par (station, mois) :
- `tnn`      = MIN(tn) sur le mois
- `tnn_date` = jour du minimum (tie-breaker : date ASC)
- `txx`      = MAX(tx) sur le mois
- `txx_date` = jour du maximum (tie-breaker : date ASC)
- `tmm`      = ROUND(AVG(tntxm), 1)

Fenêtre : `WHERE date >= date_trunc('month', now()) - interval '2 months'`.

Datetimes UTC ; comparaisons sur les valeurs renvoyées par psycopg2 via `.date()`.
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.tests.helpers.horaire import (
    fetch_v_mensuelle_realtime,
    insert_mv_quotidienne_realtime,
)

pytestmark = pytest.mark.django_db


STATION = "75114001"


def _utc_today() -> dt.date:
    return dt.datetime.now(dt.UTC).date()


def _utc_midnight(year: int, month: int, day: int) -> dt.datetime:
    return dt.datetime(year, month, day, tzinfo=dt.UTC)


def _first_of_this_month() -> dt.date:
    return _utc_today().replace(day=1)


def _first_of_previous_month() -> dt.date:
    first = _first_of_this_month()
    last_of_prev = first - dt.timedelta(days=1)
    return last_of_prev.replace(day=1)


# ---------------------------------------------------------------------------
# Agrégation simple
# ---------------------------------------------------------------------------


def test_v_mensuelle_aggregates_one_station_one_month() -> None:
    """Trois jours d'un même mois → une ligne mensuelle datée au 1er du mois."""
    first = _first_of_this_month()

    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=5.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=7.0, tx=17.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 3), tn=3.0, tx=13.0
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert len(rows) == 1
    assert rows[0]["date"].date() == first


def test_v_mensuelle_tnn_is_min_tn_of_month() -> None:
    first = _first_of_this_month()

    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=5.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=3.0, tx=17.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 3), tn=7.0, tx=15.0
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert float(rows[0]["tnn"]) == pytest.approx(3.0)


def test_v_mensuelle_txx_is_max_tx_of_month() -> None:
    first = _first_of_this_month()

    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=5.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=7.0, tx=20.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 3), tn=7.0, tx=18.0
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert float(rows[0]["txx"]) == pytest.approx(20.0)


def test_v_mensuelle_tmm_is_rounded_avg_of_tntxm() -> None:
    """tmm = ROUND(AVG(tntxm), 1) où tntxm = (tn+tx)/2."""
    first = _first_of_this_month()

    # tntxm: 10.0, 12.0, 8.4 → AVG = 10.133… → ROUND(.,1) = 10.1
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=5.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=8.0, tx=16.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 3), tn=2.4, tx=14.4
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert float(rows[0]["tmm"]) == pytest.approx(10.1)


# ---------------------------------------------------------------------------
# Tracking de tnn_date / txx_date
# ---------------------------------------------------------------------------


def test_v_mensuelle_tnn_date_is_day_of_min_tn() -> None:
    first = _first_of_this_month()

    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=5.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=3.0, tx=17.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 3), tn=7.0, tx=15.0
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert rows[0]["tnn_date"].date() == dt.date(first.year, first.month, 2)


def test_v_mensuelle_txx_date_is_day_of_max_tx() -> None:
    first = _first_of_this_month()

    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=5.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=7.0, tx=20.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 3), tn=7.0, tx=18.0
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert rows[0]["txx_date"].date() == dt.date(first.year, first.month, 2)


def test_v_mensuelle_tnn_date_tie_breaker_picks_earliest() -> None:
    """Quand plusieurs jours partagent le min tn, on prend le plus ancien."""
    first = _first_of_this_month()

    # Deux ex-aequos sur tn=3.0 (j1 et j3) → on attend j1
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=3.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=5.0, tx=17.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 3), tn=3.0, tx=15.0
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert rows[0]["tnn_date"].date() == dt.date(first.year, first.month, 1)


def test_v_mensuelle_txx_date_tie_breaker_picks_earliest() -> None:
    """Quand plusieurs jours partagent le max tx, on prend le plus ancien."""
    first = _first_of_this_month()

    # Deux ex-aequos sur tx=20.0 (j2 et j3) → on attend j2
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=5.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=7.0, tx=20.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 3), tn=7.0, tx=20.0
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert rows[0]["txx_date"].date() == dt.date(first.year, first.month, 2)


# ---------------------------------------------------------------------------
# Fenêtre "2 mois"
# ---------------------------------------------------------------------------


def test_v_mensuelle_excludes_data_older_than_2_months() -> None:
    """
    Filtre `date >= date_trunc('month', now()) - 2 months`.
    Une donnée datée de 3 mois avant le 1er du mois courant est exclue.
    """
    first_this = _first_of_this_month()
    three_months_before = first_this - dt.timedelta(days=92)
    insert_mv_quotidienne_realtime(
        STATION,
        _utc_midnight(
            three_months_before.year,
            three_months_before.month,
            three_months_before.day,
        ),
        tn=5.0,
        tx=15.0,
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert rows == []


def test_v_mensuelle_separates_stations() -> None:
    """Deux stations dans le même mois → deux lignes, agrégats indépendants."""
    first = _first_of_this_month()
    other = "31069001"

    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 1), tn=5.0, tx=15.0
    )
    insert_mv_quotidienne_realtime(
        STATION, _utc_midnight(first.year, first.month, 2), tn=7.0, tx=17.0
    )
    insert_mv_quotidienne_realtime(
        other, _utc_midnight(first.year, first.month, 1), tn=-2.0, tx=8.0
    )

    rows_a = fetch_v_mensuelle_realtime(station_code=STATION)
    rows_b = fetch_v_mensuelle_realtime(station_code=other)

    assert len(rows_a) == 1
    assert float(rows_a[0]["tnn"]) == pytest.approx(5.0)
    assert float(rows_a[0]["txx"]) == pytest.approx(17.0)
    assert len(rows_b) == 1
    assert float(rows_b[0]["tnn"]) == pytest.approx(-2.0)
    assert float(rows_b[0]["txx"]) == pytest.approx(8.0)


def test_v_mensuelle_returns_one_row_per_month_in_window() -> None:
    """Données dans 2 mois différents → 2 lignes, triées par date asc."""
    first_this = _first_of_this_month()
    first_prev = _first_of_previous_month()

    insert_mv_quotidienne_realtime(
        STATION,
        _utc_midnight(first_this.year, first_this.month, 1),
        tn=5.0,
        tx=15.0,
    )
    insert_mv_quotidienne_realtime(
        STATION,
        _utc_midnight(first_prev.year, first_prev.month, 1),
        tn=3.0,
        tx=13.0,
    )

    rows = fetch_v_mensuelle_realtime(station_code=STATION)

    assert len(rows) == 2
    assert rows[0]["date"].date() == first_prev
    assert rows[1]["date"].date() == first_this
