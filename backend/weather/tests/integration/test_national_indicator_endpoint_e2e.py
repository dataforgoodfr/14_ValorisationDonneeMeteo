"""
True end-to-end test for GET /api/v1/temperature/national-indicator.

Contrairement à `test_national_indicator_endpoint.py` (qui injecte des data
sources en mémoire), ce test sème la vraie base PostgreSQL et laisse
l'API traverser toute la pile : serializer → service → Timescale data
sources → vues SQL → données seedées.

Régression : lorsque la fenêtre demandée inclut hier et aujourd'hui,
les deux dates doivent apparaître dans `time_series`.

La vue `v_quotidienne` filtre la table brute `Quotidienne` à `< now() - 3 jours`
et compte sur la relation `mv_quotidienne_realtime` pour les jours récents.
Le conftest la crée comme table régulière (et non MV), ce qui permet
d'y INSERT directement les valeurs qu'auraient produites pg_cron en prod.
"""

from __future__ import annotations

import datetime as dt

import pytest
from django.db import connection
from django.urls import reverse
from rest_framework.test import APIClient

from weather.bootstrap_itn import ITNDependencyProvider
from weather.services.national_indicator.stations import expected_station_codes
from weather.tests.helpers.itn import insert_itn_daily
from weather.tests.helpers.itn_baseline import insert_daily_baseline
from weather.tests.helpers.stations import insert_station

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def reset_itn_dependency_provider() -> None:
    # Garantit qu'on utilise les data sources Timescale par défaut, même si
    # un test précédent a installé un builder en mémoire.
    ITNDependencyProvider.reset()
    yield
    ITNDependencyProvider.reset()


def _insert_realtime_row(day: dt.date, code: str, tntxm: float) -> None:
    midnight_utc = dt.datetime.combine(day, dt.time.min, tzinfo=dt.UTC)
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_quotidienne_realtime
                (station_code, date, tntxm, tn, tx)
            VALUES
                (%(code)s, %(date)s, %(tntxm)s, NULL, NULL)
            """,
            {"code": code, "date": midnight_utc, "tntxm": tntxm},
        )


def _seed_complete_itn_day_realtime(day: dt.date, value: float) -> None:
    """Sème les 30 stations ITN attendues pour `day` côté realtime."""
    for code in expected_station_codes(day):
        insert_station(code)
        _insert_realtime_row(day, code, value)


def test_national_indicator_endpoint_returns_today_and_yesterday(
    client: APIClient,
) -> None:
    today = dt.datetime.now(dt.UTC).date()
    yesterday = today - dt.timedelta(days=1)

    # 1. Observé : 30 stations ITN pour hier et aujourd'hui, via le chemin
    #    realtime (puisque v_quotidienne exclut Quotidienne sur < 3 jours).
    _seed_complete_itn_day_realtime(yesterday, value=10.0)
    _seed_complete_itn_day_realtime(today, value=12.0)

    # 2. Baseline 1991-2020 pour chacune des deux (month, day_of_month).
    #    `yesterday` et `today` ayant toujours des (month, day) distincts,
    #    on insère inconditionnellement les deux.
    insert_daily_baseline(month=yesterday.month, day=yesterday.day, mean=10.0, std=2.0)
    insert_daily_baseline(month=today.month, day=today.day, mean=10.0, std=2.0)

    # 3. Historique ITN journalier pour alimenter v_itn_absolute_extremes_daily.
    #    Le service exige un extremum pour chaque (month, day) renvoyé.
    for d in (yesterday, today):
        insert_itn_daily(2000, d.month, d.day, 5.0)
        insert_itn_daily(2015, d.month, d.day, 15.0)

    url = reverse("temperature-national-indicator")
    resp = client.get(
        url,
        {
            "date_start": yesterday.isoformat(),
            "date_end": today.isoformat(),
            "granularity": "day",
        },
    )

    assert resp.status_code == 200, resp.json()

    time_series = resp.json()["time_series"]
    dates_returned = [point["date"] for point in time_series]

    assert yesterday.isoformat() in dates_returned, (
        f"Yesterday ({yesterday.isoformat()}) is missing from time_series. "
        f"Got dates: {dates_returned}"
    )
    assert today.isoformat() in dates_returned, (
        f"Today ({today.isoformat()}) is missing from time_series. "
        f"Got dates: {dates_returned}"
    )
