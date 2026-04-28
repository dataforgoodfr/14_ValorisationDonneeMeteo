import pytest
from rest_framework.test import APIClient

from weather.bootstrap_temperature_minmax import (
    TemperatureMinMaxOverviewDependencyProvider,
)
from weather.data_sources.temperature_minmax_fake import (
    FakeTemperatureMinMaxOverviewDataSource,
)

URL = "/api/v1/temperature/extremes"


@pytest.fixture(autouse=True)
def use_fake_datasource():
    TemperatureMinMaxOverviewDependencyProvider.set_builder(
        lambda: FakeTemperatureMinMaxOverviewDataSource()
    )
    yield
    TemperatureMinMaxOverviewDependencyProvider.reset()


@pytest.fixture
def client() -> APIClient:
    return APIClient()


def test_happy_path(client: APIClient):
    resp = client.get(URL, {"date_start": "2024-01-01", "date_end": "2024-12-31"})

    assert resp.status_code == 200
    data = resp.json()

    assert "metadata" in data
    assert "pagination" in data
    assert "stations" in data
    assert isinstance(data["stations"], list)
    assert len(data["stations"]) > 0


def test_metadata_fields(client: APIClient):
    resp = client.get(
        URL,
        {"date_start": "2024-01-01", "date_end": "2024-12-31", "type": "tmin"},
    )

    assert resp.status_code == 200
    meta = resp.json()["metadata"]

    assert meta["date_start"] == "2024-01-01"
    assert meta["date_end"] == "2024-12-31"
    assert meta["type"] == "tmin"
    assert "filters" in meta
    assert "ordering" in meta


def test_station_fields_present(client: APIClient):
    resp = client.get(URL, {"date_start": "2024-01-01", "date_end": "2024-12-31"})

    assert resp.status_code == 200
    s = resp.json()["stations"][0]

    assert "station_id" in s
    assert "station_name" in s
    assert "textreme_mean" in s
    assert "tmean_mean" in s
    assert "lat" in s
    assert "lon" in s
    assert "alt" in s
    assert "department" in s
    assert "region" in s
    assert "classe" in s
    assert "annee_de_creation" in s
    assert "annee_de_fermeture" in s


def test_returns_400_missing_date_start(client: APIClient):
    resp = client.get(URL, {"date_end": "2024-12-31"})

    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_PARAMETER"
    assert "date_start" in resp.json()["error"]["details"]


def test_returns_400_missing_date_end(client: APIClient):
    resp = client.get(URL, {"date_start": "2024-01-01"})

    assert resp.status_code == 400
    assert "date_end" in resp.json()["error"]["details"]


def test_returns_400_date_end_before_date_start(client: APIClient):
    resp = client.get(URL, {"date_start": "2024-12-31", "date_end": "2024-01-01"})

    assert resp.status_code == 400
    assert "date_end" in resp.json()["error"]["details"]


def test_returns_400_invalid_type(client: APIClient):
    resp = client.get(
        URL, {"date_start": "2024-01-01", "date_end": "2024-12-31", "type": "tmean"}
    )

    assert resp.status_code == 400
    assert "type" in resp.json()["error"]["details"]


def test_returns_400_textreme_min_greater_than_max(client: APIClient):
    resp = client.get(
        URL,
        {
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "textreme_min": 30,
            "textreme_max": 20,
        },
    )

    assert resp.status_code == 400
    assert "textreme_max" in resp.json()["error"]["details"]


def test_returns_400_negative_offset(client: APIClient):
    resp = client.get(
        URL, {"date_start": "2024-01-01", "date_end": "2024-12-31", "offset": -1}
    )

    assert resp.status_code == 400


def test_pagination_fields(client: APIClient):
    resp = client.get(
        URL,
        {"date_start": "2024-01-01", "date_end": "2024-12-31", "limit": 2, "offset": 1},
    )

    assert resp.status_code == 200
    p = resp.json()["pagination"]

    assert p["limit"] == 2
    assert p["offset"] == 1
    assert "total_count" in p
    assert len(resp.json()["stations"]) <= 2


def test_type_tmax_default(client: APIClient):
    resp = client.get(URL, {"date_start": "2024-01-01", "date_end": "2024-12-31"})

    assert resp.status_code == 200
    assert resp.json()["metadata"]["type"] == "tmax"


def test_type_tmin_accepted(client: APIClient):
    resp = client.get(
        URL, {"date_start": "2024-01-01", "date_end": "2024-12-31", "type": "tmin"}
    )

    assert resp.status_code == 200
    assert resp.json()["metadata"]["type"] == "tmin"


def test_filters_echoed_in_metadata(client: APIClient):
    resp = client.get(
        URL,
        {
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "station_ids": "07149,07222",
            "departments": "69,75",
            "textreme_min": 20,
        },
    )

    assert resp.status_code == 200
    filters = resp.json()["metadata"]["filters"]

    assert filters["station_ids"] == ["07149", "07222"]
    assert filters["departments"] == ["69", "75"]
    assert filters["textreme_min"] == 20.0


def test_ordering_echoed_in_metadata(client: APIClient):
    resp = client.get(
        URL,
        {
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "ordering": "station_name",
        },
    )

    assert resp.status_code == 200
    assert resp.json()["metadata"]["ordering"] == "station_name"


def test_empty_result_returns_200(client: APIClient):
    resp = client.get(
        URL,
        {"date_start": "2024-01-01", "date_end": "2024-12-31", "offset": 9999},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["stations"] == []
