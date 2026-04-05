import pytest
from rest_framework.test import APIClient

from weather.bootstrap_temperature_deviation import (
    TemperatureDeviationOverviewDependencyProvider,
)
from weather.data_sources.temperature_deviation_fake import (
    FakeTemperatureDeviationOverviewDataSource,
)


@pytest.fixture(autouse=True)
def use_fake_datasource():
    TemperatureDeviationOverviewDependencyProvider.set_builder(
        lambda: FakeTemperatureDeviationOverviewDataSource()
    )
    yield
    TemperatureDeviationOverviewDependencyProvider.reset()


@pytest.fixture
def client() -> APIClient:
    return APIClient()


def _url() -> str:
    return "/api/v1/temperature/deviation"


def test_overview_endpoint_happy_path(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
        },
    )

    assert resp.status_code == 200
    data = resp.json()

    assert "metadata" in data
    assert "national" in data
    assert "pagination" in data
    assert "stations" in data

    assert data["metadata"]["baseline"] == "1991-2020"
    assert isinstance(data["stations"], list)
    assert len(data["stations"]) > 0


def test_overview_endpoint_returns_400_on_invalid_dates(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-04-01",
            "date_end": "2025-03-01",
        },
    )

    assert resp.status_code == 400
    data = resp.json()
    assert "error" in data


def test_overview_endpoint_returns_400_on_invalid_bounds(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "temperature_mean_min": 30,
            "temperature_mean_max": 10,
        },
    )

    assert resp.status_code == 400


def test_overview_endpoint_pagination(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "page": 2,
            "page_size": 10,
        },
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["pagination"]["page"] == 2
    assert data["pagination"]["page_size"] == 10
    assert len(data["stations"]) <= 10


def test_overview_endpoint_ordering(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "ordering": "-deviation",
        },
    )

    assert resp.status_code == 200
    stations = resp.json()["stations"]

    assert len(stations) >= 2
    assert stations[0]["deviation"] >= stations[1]["deviation"]


def test_overview_endpoint_filters(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "deviation_min": 2,
        },
    )

    assert resp.status_code == 200
    stations = resp.json()["stations"]

    assert all(s["deviation"] >= 2 for s in stations)


def test_overview_endpoint_empty_result(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "deviation_min": 999,
        },
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["stations"] == []
    assert data["pagination"]["total_count"] == 0
