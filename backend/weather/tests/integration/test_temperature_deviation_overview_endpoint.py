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
            "offset": 10,
            "limit": 10,
        },
    )

    assert resp.status_code == 200
    data = resp.json()

    assert data["pagination"]["offset"] == 10
    assert data["pagination"]["limit"] == 10
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


def test_overview_endpoint_returns_added_station_fields(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
        },
    )

    assert resp.status_code == 200
    station = resp.json()["stations"][0]

    assert "lat" in station
    assert "lon" in station
    assert "department" in station
    assert "alt" in station
    assert "region" in station


def test_overview_endpoint_filters_by_department(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "departments": "13",
        },
    )

    assert resp.status_code == 200
    stations = resp.json()["stations"]

    assert all(s["department"] == "13" for s in stations)


def test_overview_endpoint_national_is_independent_from_station_filters(
    client: APIClient,
):
    resp_all = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
        },
    )
    resp_filtered = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "departments": "13",
        },
    )

    assert resp_all.status_code == 200
    assert resp_filtered.status_code == 200
    assert (
        resp_all.json()["national"]["deviation_mean"]
        == resp_filtered.json()["national"]["deviation_mean"]
    )


def test_overview_endpoint_returns_400_on_negative_offset(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "offset": -1,
        },
    )

    assert resp.status_code == 400


def test_overview_endpoint_returns_400_on_limit_too_large(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "limit": 1000,
        },
    )

    assert resp.status_code == 400


def test_overview_endpoint_filters_by_station_ids(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "station_ids": "70000,70001",
            "limit": 50,
            "offset": 0,
        },
    )

    assert resp.status_code == 200
    stations = resp.json()["stations"]

    assert {s["station_id"] for s in stations} == {"70000", "70001"}


def test_overview_endpoint_combines_station_ids_and_station_search(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "station_ids": "70010,70011",
            "station_search": "70010",
            "limit": 50,
            "offset": 0,
        },
    )

    assert resp.status_code == 200
    stations = resp.json()["stations"]

    assert len(stations) == 1
    assert stations[0]["station_id"] == "70010"


def test_overview_endpoint_echoes_station_ids_in_metadata_filters(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "station_ids": "70000,70001",
        },
    )

    assert resp.status_code == 200
    assert resp.json()["metadata"]["filters"]["station_ids"] == ["70000", "70001"]


def test_overview_endpoint_ordering_by_department(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "ordering": "department",
        },
    )

    assert resp.status_code == 200
    stations = resp.json()["stations"]

    assert len(stations) >= 2
    assert stations[0]["department"] <= stations[1]["department"]


def test_overview_endpoint_ordering_by_region(client: APIClient):
    resp = client.get(
        _url(),
        {
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "ordering": "region",
        },
    )

    assert resp.status_code == 200
    stations = resp.json()["stations"]

    assert len(stations) >= 2
    assert stations[0]["region"] <= stations[1]["region"]
