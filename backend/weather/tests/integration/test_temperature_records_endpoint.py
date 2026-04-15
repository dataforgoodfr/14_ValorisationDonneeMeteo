import pytest
from rest_framework.test import APIClient

from weather.bootstrap_temperature_records import (
    TemperatureRecordsDependencyProvider,
)
from weather.data_sources.temperature_records_fake import (
    FakeTemperatureRecordsDataSource,
)


@pytest.fixture
def fake_temperature_records_dep():
    TemperatureRecordsDependencyProvider.set_builder(
        lambda: FakeTemperatureRecordsDataSource()
    )
    try:
        yield
    finally:
        TemperatureRecordsDependencyProvider.reset()


@pytest.mark.usefixtures("fake_temperature_records_dep")
def test_get_records_all_time_hot_happy_path(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {"type_records": "hot"},
    )

    assert resp.status_code == 200
    body = resp.json()

    assert isinstance(body, list)
    assert len(body) >= 5

    first = body[0]
    assert "station_id" in first
    assert "station_name" in first
    assert "department" in first
    assert "record_value" in first
    assert "record_date" in first
    assert "lat" in first
    assert "lon" in first
    assert "alt" in first


@pytest.mark.usefixtures("fake_temperature_records_dep")
def test_get_records_defaults_to_all_time_hot(client: APIClient):
    resp = client.get("/api/v1/temperature/records")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) >= 5
    # Default is hot, so all values should be >= 30
    assert all(entry["record_value"] >= 30 for entry in body)


@pytest.mark.usefixtures("fake_temperature_records_dep")
def test_get_records_cold(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {"type_records": "cold"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert all(entry["record_value"] <= 0 for entry in body)


@pytest.mark.usefixtures("fake_temperature_records_dep")
def test_get_records_month_happy_path(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {"period_type": "month", "month": 7, "type_records": "hot"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


@pytest.mark.usefixtures("fake_temperature_records_dep")
def test_get_records_season_happy_path(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {"period_type": "season", "season": "winter", "type_records": "cold"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


def test_get_records_returns_400_if_period_type_month_without_month(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/records",
        {"period_type": "month", "type_records": "hot"},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "month" in body["error"]["details"]


def test_get_records_returns_400_if_period_type_season_without_season(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/records",
        {"period_type": "season", "type_records": "cold"},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "season" in body["error"]["details"]


def test_get_records_returns_400_if_unknown_period_type(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {"period_type": "weekly"},
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"


@pytest.mark.usefixtures("fake_temperature_records_dep")
def test_get_records_endpoint_uses_dependency_provider(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {"period_type": "all_time", "type_records": "hot"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 5
    assert body[0]["station_id"]  # non-empty string
