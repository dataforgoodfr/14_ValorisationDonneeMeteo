from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from weather.bootstrap_temperature_absolute_records import (
    TemperatureAbsoluteRecordsDependencyProvider,
)
from weather.services.temperature_records.protocols import (
    TemperatureAbsoluteRecordsDataSource,
)
from weather.services.temperature_records.types import (
    Pagination,
    TemperatureRecordEntry,
    TemperatureRecordsRequest,
    TemperatureRecordsResult,
)

ENDPOINT = reverse("temperature-records-absolute")


class _FakeTemperatureAbsoluteRecordsDataSource(TemperatureAbsoluteRecordsDataSource):
    """Fake qui retourne un result fixe quelle que soit la request."""

    def __init__(self, result: TemperatureRecordsResult) -> None:
        self._result = result

    def fetch_records(
        self, request: TemperatureRecordsRequest
    ) -> TemperatureRecordsResult:
        return self._result


def given_this_data(result: TemperatureRecordsResult) -> None:
    """Câble le fake pour retourner ce result quel que soit le request."""
    TemperatureAbsoluteRecordsDependencyProvider.set_builder(
        lambda: _FakeTemperatureAbsoluteRecordsDataSource(result)
    )


@pytest.fixture(autouse=True)
def _reset_absolute_records_dep():
    yield
    TemperatureAbsoluteRecordsDependencyProvider.reset()


def _entry(**overrides) -> TemperatureRecordEntry:
    defaults = {
        "station_id": "07149",
        "station_name": "ORLY",
        "department": "94",
        "record_value": 42.0,
        "record_date": dt.date(2019, 7, 25),
        "lat": 48.718,
        "lon": 2.397,
        "alt": 86.0,
        "classe_recente": 1,
        "date_de_creation": dt.date(1921, 1, 1),
        "date_de_fermeture": None,
    }
    defaults.update(overrides)
    return TemperatureRecordEntry(**defaults)


def _result(entries: list[TemperatureRecordEntry]) -> TemperatureRecordsResult:
    return TemperatureRecordsResult(
        entries=entries,
        pagination=Pagination(
            total_count=len(entries),
            page=1,
            page_size=50,
            total_pages=1 if entries else 0,
        ),
    )


# =========================
# Happy paths
# =========================


def test_records_happy_path_all_time_hot(client: APIClient):
    given_this_data(
        _result(
            [
                _entry(
                    station_id="07149",
                    station_name="ORLY",
                    record_value=42.6,
                    record_date=dt.date(2019, 7, 25),
                )
            ]
        )
    )

    resp = client.get(
        ENDPOINT,
        {"period_type": "all_time", "type_records": "hot"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"]["total_count"] == 1
    assert len(body["results"]) == 1
    assert body["results"][0]["station_id"] == "07149"
    assert body["results"][0]["station_name"] == "ORLY"
    assert body["results"][0]["record_value"] == 42.6
    assert body["results"][0]["record_date"] == "2019-07-25"


def test_records_happy_path_month_with_specific_month(client: APIClient):
    given_this_data(_result([_entry(record_value=38.0)]))

    resp = client.get(
        ENDPOINT,
        {"period_type": "month", "month": "7", "type_records": "hot"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) == 1
    assert body["results"][0]["record_value"] == 38.0


def test_records_happy_path_season_with_specific_season(client: APIClient):
    given_this_data(_result([_entry(record_value=44.0)]))

    resp = client.get(
        ENDPOINT,
        {"period_type": "season", "season": "summer", "type_records": "hot"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) == 1
    assert body["results"][0]["record_value"] == 44.0


def test_records_defaults_apply_when_no_params(client: APIClient):
    """period_type=all_time et type_records=hot ont des defaults : l'endpoint accepte une requête vide."""
    given_this_data(_result([]))

    resp = client.get(ENDPOINT)

    assert resp.status_code == 200


# =========================
# Pass-through de paramètres
# =========================


def test_records_period_type_month_without_month_returns_200(client: APIClient):
    """period_type=month sans month est supporté (records de tous les mois)."""
    given_this_data(_result([]))

    resp = client.get(ENDPOINT, {"period_type": "month", "type_records": "hot"})

    assert resp.status_code == 200


def test_records_period_type_season_without_season_returns_200(client: APIClient):
    """period_type=season sans season est supporté (records de toutes les saisons)."""
    given_this_data(_result([]))

    resp = client.get(ENDPOINT, {"period_type": "season", "type_records": "hot"})

    assert resp.status_code == 200


def test_records_type_records_cold_accepts_param(client: APIClient):
    given_this_data(_result([_entry(record_value=-20.5)]))

    resp = client.get(ENDPOINT, {"type_records": "cold"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["results"][0]["record_value"] == -20.5


# =========================
# Territoire
# =========================


def test_records_territoire_department_accepts_param(client: APIClient):
    given_this_data(_result([]))

    resp = client.get(
        ENDPOINT,
        {"territoire": "department", "territoire_id": "94"},
    )

    assert resp.status_code == 200


def test_records_territoire_station_accepts_param(client: APIClient):
    given_this_data(_result([]))

    resp = client.get(
        ENDPOINT,
        {"territoire": "station", "territoire_id": "07149"},
    )

    assert resp.status_code == 200


def test_records_territoire_region_accepts_param(client: APIClient):
    given_this_data(_result([]))

    resp = client.get(
        ENDPOINT,
        {"territoire": "region", "territoire_id": "11"},
    )

    assert resp.status_code == 200


# =========================
# Sérialisation des entrées
# =========================


def test_records_serializes_entry_with_expected_fields(client: APIClient):
    given_this_data(
        _result(
            [
                _entry(
                    station_id="07149",
                    station_name="ORLY",
                    department="94",
                    record_value=42.6,
                    record_date=dt.date(2019, 7, 25),
                    lat=48.718,
                    lon=2.397,
                    alt=86.0,
                    classe_recente=1,
                    date_de_creation=dt.date(1921, 1, 1),
                    date_de_fermeture=None,
                )
            ]
        )
    )

    resp = client.get(ENDPOINT)

    assert resp.status_code == 200
    r = resp.json()["results"][0]
    assert r["station_id"] == "07149"
    assert r["station_name"] == "ORLY"
    assert r["department"] == "94"
    assert r["record_value"] == 42.6
    assert r["record_date"] == "2019-07-25"
    assert r["lat"] == 48.718
    assert r["lon"] == 2.397
    assert r["alt"] == 86.0
    assert r["classe_recente"] == 1
    assert r["date_de_creation"] == "1921-01-01"
    assert r["date_de_fermeture"] is None


def test_records_serializes_date_de_fermeture_when_present(client: APIClient):
    given_this_data(_result([_entry(date_de_fermeture=dt.date(2010, 6, 30))]))

    resp = client.get(ENDPOINT)

    assert resp.status_code == 200
    assert resp.json()["results"][0]["date_de_fermeture"] == "2010-06-30"


def test_records_serializes_pagination(client: APIClient):
    given_this_data(
        TemperatureRecordsResult(
            entries=[],
            pagination=Pagination(
                total_count=123, page=2, page_size=10, total_pages=13
            ),
        )
    )

    resp = client.get(ENDPOINT, {"page": "2", "page_size": "10"})

    assert resp.status_code == 200
    p = resp.json()["pagination"]
    assert p["total_count"] == 123
    assert p["page"] == 2
    assert p["page_size"] == 10
    assert p["total_pages"] == 13


def test_records_serializes_empty_results(client: APIClient):
    given_this_data(_result([]))

    resp = client.get(ENDPOINT)

    assert resp.status_code == 200
    body = resp.json()
    assert body["results"] == []
    assert body["pagination"]["total_count"] == 0


# =========================
# Erreurs 400
# =========================


def test_records_territoire_without_id_returns_400(client: APIClient):
    resp = client.get(ENDPOINT, {"territoire": "department"})

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "territoire_id" in body["error"]["details"]


def test_records_invalid_period_type_returns_400(client: APIClient):
    resp = client.get(ENDPOINT, {"period_type": "week"})

    assert resp.status_code == 400


def test_records_invalid_type_records_returns_400(client: APIClient):
    resp = client.get(ENDPOINT, {"type_records": "tepid"})

    assert resp.status_code == 400


def test_records_invalid_sort_field_returns_400(client: APIClient):
    resp = client.get(ENDPOINT, {"sort": "bad_field"})

    assert resp.status_code == 400


def test_records_invalid_month_returns_400(client: APIClient):
    resp = client.get(ENDPOINT, {"period_type": "month", "month": "13"})

    assert resp.status_code == 400


def test_records_invalid_season_returns_400(client: APIClient):
    resp = client.get(ENDPOINT, {"period_type": "season", "season": "monsoon"})

    assert resp.status_code == 400


def test_records_date_start_without_date_end_returns_400(client: APIClient):
    resp = client.get(ENDPOINT, {"date_start": "2019-01-01"})

    assert resp.status_code == 400


def test_records_classe_recente_min_greater_than_max_returns_400(client: APIClient):
    resp = client.get(
        ENDPOINT,
        {"classe_recente_min": "3", "classe_recente_max": "1"},
    )

    assert resp.status_code == 400
