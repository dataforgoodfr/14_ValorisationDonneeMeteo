"""
E2E pour /api/v1/temperature/records/graph contre le vrai HybridRecordsGraphDataSource.

Reproduit le bug observé en staging :
    https://staging.dataclimat.fr/api/v1/temperature/records/graph
        ?date_start=2025-01-01&date_end=2026-05-22
        &granularity=year&type_records=all
        &period_type=month&month=5&territoire=france

Un record (TX) battu via une nouvelle valeur dans v_quotidienne (post-refresh
mv_quotidienne_realtime) après la cutoff_date doit apparaître dans la réponse.
"""

from __future__ import annotations

import datetime as dt

import pytest
from rest_framework.test import APIClient

from weather.tests.helpers.horaire import insert_mv_quotidienne_realtime
from weather.tests.helpers.records import (
    insert_mv_record,
    insert_mv_records_absolus_par_mois,
    set_cutoff,
)
from weather.tests.helpers.stations import insert_station

# NB : ces tests vérifient l'enrichissement post-cutoff via le hybrid graph.
# Bootstrap actuel utilise le data source MV-only, donc le endpoint en prod ne
# passe plus par ce code path. Tests conservés pour la ré-activation future.

URL = "/api/v1/temperature/records/graph"


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_new_record_via_v_quotidienne_appears_in_endpoint_response(client: APIClient):
    code = "75114002"
    insert_station(code, "Station Endpoint Hybrid", departement=75)

    # Record historique figé dans la MV (mai, period_type=month, period_value="5")
    insert_mv_record(
        station_code=code,
        station_name="Station Endpoint Hybrid",
        period_type="month",
        period_value="5",
        record_type="TX",
        value=38.0,
        date=dt.date(2003, 5, 15),
        department=75,
    )
    set_cutoff(dt.date(2025, 12, 31))

    # Nouvelle valeur dans v_quotidienne (état post-refresh mv_quotidienne_realtime)
    # qui bat le record de 38.0 → doit être détectée comme nouveau record battu.
    insert_mv_quotidienne_realtime(code, dt.date(2026, 5, 15), tn=5.0, tx=45.0)

    resp = client.get(
        URL,
        {
            "date_start": "2025-01-01",
            "date_end": "2026-05-22",
            "granularity": "year",
            "type_records": "all",
            "period_type": "month",
            "month": "5",
            "territoire": "france",
        },
    )

    assert resp.status_code == 200, resp.content
    body = resp.json()

    records_for_station = [
        r for r in body["records"] if r["station_id"].strip() == code
    ]
    new_record = next(
        (r for r in records_for_station if r["date"] == "2026-05-15"), None
    )
    assert new_record is not None, (
        f"Le nouveau record du 2026-05-15 manque dans la réponse : "
        f"{records_for_station}"
    )
    assert new_record["valeur"] == 45.0
    assert new_record["type_records"] == "hot"

    bucket_2026 = next(b for b in body["buckets"] if b["bucket"] == "2026")
    assert bucket_2026["nb_records_battus"] >= 1


@pytest.mark.django_db
def test_real_new_records_via_endpoint_with_absolute_seed(client: APIClient):
    """Réplique du URL staging :
    /api/v1/temperature/records/graph
        ?date_start=2025-01-01&date_end=2026-05-22
        &granularity=year&type_records=all
        &period_type=month&month=5&territoire=france

    Station type MARIGNANE : record absolu May en mv_records_absolus_par_mois
    (rien dans mv_records_battus à cause du filtre 50-ans). Une lecture du
    jour qui bat ce record (en TX comme en TN) doit apparaître dans la réponse.
    """
    code = "13054006"
    insert_station(
        code,
        "MARIGNANE Test",
        departement=13,
        first_temperature_date=dt.date(1920, 1, 1),
    )
    # Records absolus en mv_records_absolus_par_mois ; rien en mv_records_battus
    insert_mv_records_absolus_par_mois(
        station_code=code,
        month=5,
        txx_max=35.0,
        txx_max_date=dt.date(2000, 5, 15),
        tnn_min=0.0,
        tnn_min_date=dt.date(1960, 5, 1),
    )
    set_cutoff(dt.date(2025, 12, 31))
    # TX=42 bat 35 (vrai hot record), TN=-3 bat 0 (vrai cold record)
    insert_mv_quotidienne_realtime(code, dt.date(2026, 5, 22), tn=-3.0, tx=42.0)

    resp = client.get(
        URL,
        {
            "date_start": "2025-01-01",
            "date_end": "2026-05-22",
            "granularity": "year",
            "type_records": "all",
            "period_type": "month",
            "month": "5",
            "territoire": "france",
        },
    )

    assert resp.status_code == 200, resp.content
    body = resp.json()

    for_station = [
        r
        for r in body["records"]
        if r["station_id"].strip() == code and r["date"] == "2026-05-22"
    ]
    hot = [r for r in for_station if r["type_records"] == "hot"]
    cold = [r for r in for_station if r["type_records"] == "cold"]
    assert (
        len(hot) == 1 and hot[0]["valeur"] == 42.0
    ), f"42°C bat le record May 35°C, devrait apparaître : {for_station}"
    assert (
        len(cold) == 1 and cold[0]["valeur"] == -3.0
    ), f"-3°C bat le record May 0°C, devrait apparaître : {for_station}"


@pytest.mark.django_db
def test_today_record_appears_when_period_type_month_without_month(
    client: APIClient,
):
    """
    Bug reproduit depuis :
    https://staging.dataclimat.fr/api/v1/temperature/records/graph
        ?type_records=hot&granularity=day
        &date_start=2026-05-22&date_end=2026-05-22
        &period_type=month

    Quand period_type=month sans paramètre month (mode "tous les mois"), le
    record du jour poussé dans mv_quotidienne_realtime doit néanmoins
    apparaître dans la réponse, comparé au seed du mois en cours.
    """
    today = dt.date.today()

    code = "75114003"
    insert_station(code, "Station Today Record", departement=75)

    # Record historique pour le mois courant (period_type=month, period_value=
    # numéro du mois en cours)
    insert_mv_record(
        station_code=code,
        station_name="Station Today Record",
        period_type="month",
        period_value=str(today.month),
        record_type="TX",
        value=38.0,
        date=today.replace(year=2003),
        department=75,
    )
    set_cutoff(today - dt.timedelta(days=180))

    insert_mv_quotidienne_realtime(code, today, tn=5.0, tx=45.0)

    resp = client.get(
        URL,
        {
            "date_start": today.isoformat(),
            "date_end": today.isoformat(),
            "granularity": "day",
            "type_records": "hot",
            "period_type": "month",
        },
    )

    assert resp.status_code == 200, resp.content
    body = resp.json()

    records_for_station = [
        r for r in body["records"] if r["station_id"].strip() == code
    ]
    new_record = next(
        (r for r in records_for_station if r["date"] == today.isoformat()), None
    )
    assert new_record is not None, (
        f"Le record du jour ({today.isoformat()}) manque dans la réponse. "
        f"Records de la station : {records_for_station}"
    )
    assert new_record["valeur"] == 45.0
    assert new_record["type_records"] == "hot"
