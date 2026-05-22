"""
Tests d'intégration de la vue SQL `v_quotidienne`.

`v_quotidienne` UNIONe deux sources :
- la "MV" `mv_quotidienne_realtime` (en test : une table régulière, voir conftest)
- la table brute `Quotidienne`, filtrée à `AAAAMMJJ < now() - 3 jours`

Les datetimes sont construits en UTC (`dt.UTC`) ; les comparaisons sur les
valeurs renvoyées par psycopg2 utilisent `.date()` pour rester insensibles
à la conversion timestamp ↔ timestamptz côté Postgres.
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.tests.helpers.horaire import (
    fetch_v_quotidienne,
    insert_mv_quotidienne_realtime,
)
from weather.tests.helpers.quotidienne import insert_quotidienne

pytestmark = pytest.mark.django_db


STATION = "75114001"


def _utc_today() -> dt.date:
    return dt.datetime.now(dt.UTC).date()


def _utc_midnight(date: dt.date) -> dt.datetime:
    return dt.datetime.combine(date, dt.time.min, tzinfo=dt.UTC)


# ---------------------------------------------------------------------------
# Sources : MV vs table brute
# ---------------------------------------------------------------------------


def test_v_quotidienne_returns_recent_data_from_realtime_mv():
    """Les jours récents (dans les 3 derniers jours) viennent du MV temps réel."""
    today = _utc_today()
    insert_mv_quotidienne_realtime(STATION, _utc_midnight(today), tn=8.0, tx=17.0)

    rows = fetch_v_quotidienne(station_code=STATION)

    assert len(rows) == 1
    assert rows[0]["date"].date() == today
    assert float(rows[0]["tntxm"]) == pytest.approx(12.5)
    assert float(rows[0]["tn"]) == pytest.approx(8.0)
    assert float(rows[0]["tx"]) == pytest.approx(17.0)


def test_v_quotidienne_returns_old_data_from_raw_quotidienne():
    """Les jours anciens (> 3 jours) viennent de la table brute `Quotidienne`."""
    five_days_ago = _utc_today() - dt.timedelta(days=5)
    insert_quotidienne(_utc_midnight(five_days_ago), STATION, tx=20.0, tn=10.0)

    rows = fetch_v_quotidienne(station_code=STATION)

    assert len(rows) == 1
    assert rows[0]["date"].date() == five_days_ago
    assert float(rows[0]["tntxm"]) == pytest.approx(15.0)


# ---------------------------------------------------------------------------
# Frontière "3 jours" sur la table brute
# ---------------------------------------------------------------------------


def test_v_quotidienne_excludes_raw_within_last_3_days():
    """
    Les lignes brutes (Quotidienne) avec `AAAAMMJJ` dans les 3 derniers jours
    sont exclues — on attend que la donnée vienne du MV temps réel.
    """
    two_days_ago = _utc_today() - dt.timedelta(days=2)
    insert_quotidienne(_utc_midnight(two_days_ago), STATION, tx=20.0, tn=10.0)

    rows = fetch_v_quotidienne(station_code=STATION)

    assert rows == []


def test_v_quotidienne_excludes_raw_at_exact_3_day_boundary():
    """
    Frontière stricte : `AAAAMMJJ < now() - 3 jours`.
    Une ligne brute datée d'exactement 3 jours (00:00) est EXCLUE.
    """
    three_days_ago_midnight = _utc_midnight(_utc_today() - dt.timedelta(days=3))
    insert_quotidienne(three_days_ago_midnight, STATION, tx=20.0, tn=10.0)

    rows = fetch_v_quotidienne(station_code=STATION)

    assert rows == []


# ---------------------------------------------------------------------------
# UNION ALL + multi-stations
# ---------------------------------------------------------------------------


def test_v_quotidienne_combines_mv_and_raw_in_same_query():
    """Un jour récent (MV) et un jour ancien (brut) cohabitent dans la vue."""
    today = _utc_today()
    five_days_ago = today - dt.timedelta(days=5)

    insert_mv_quotidienne_realtime(STATION, _utc_midnight(today), tn=8.0, tx=17.0)
    insert_quotidienne(_utc_midnight(five_days_ago), STATION, tx=22.0, tn=12.0)

    rows = fetch_v_quotidienne(station_code=STATION)

    assert len(rows) == 2
    dates = [r["date"].date() for r in rows]
    assert dates[0] == five_days_ago
    assert dates[1] == today


def test_v_quotidienne_returns_all_stations_independently():
    other = "31069001"
    today_midnight = _utc_midnight(_utc_today())

    insert_mv_quotidienne_realtime(STATION, today_midnight, tn=5.0, tx=15.0)
    insert_mv_quotidienne_realtime(other, today_midnight, tn=15.0, tx=25.0)

    rows_a = fetch_v_quotidienne(station_code=STATION)
    rows_b = fetch_v_quotidienne(station_code=other)

    assert len(rows_a) == 1
    assert float(rows_a[0]["tntxm"]) == pytest.approx(10.0)
    assert len(rows_b) == 1
    assert float(rows_b[0]["tntxm"]) == pytest.approx(20.0)
