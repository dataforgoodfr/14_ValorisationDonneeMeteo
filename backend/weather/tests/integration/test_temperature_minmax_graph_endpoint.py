import pytest
from rest_framework.test import APIClient

from weather.bootstrap_temperature_minmax import TemperatureMinMaxDependencyProvider
from weather.data_sources.temperature_minmax_fake import FakeTemperatureMinMaxDataSource

URL = "/api/v1/temperature/minmax/graph"


@pytest.fixture
def fake_minmax_dep():
    TemperatureMinMaxDependencyProvider.set_builder(
        lambda: FakeTemperatureMinMaxDataSource()
    )
    try:
        yield
    finally:
        TemperatureMinMaxDependencyProvider.reset()


def test_returns_400_when_no_params(client: APIClient):
    resp = client.get(URL)

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "date_start" in body["error"]["details"]
    assert "date_end" in body["error"]["details"]
    assert "granularity" in body["error"]["details"]


def test_returns_400_when_date_end_before_date_start(client: APIClient):
    resp = client.get(
        URL,
        {
            "date_start": "2020-12-31",
            "date_end": "2020-01-01",
            "granularity": "month",
        },
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "date_end" in body["error"]["details"]


def test_returns_400_on_invalid_granularity(client: APIClient):
    resp = client.get(
        URL,
        {
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "granularity": "week",
        },
    )

    assert resp.status_code == 400


@pytest.mark.usefixtures("fake_minmax_dep")
def test_france_returns_national_series(client: APIClient):
    resp = client.get(
        URL,
        {
            "date_start": "2020-01-01",
            "date_end": "2020-03-31",
            "granularity": "month",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert "national" in body
    assert body["stations"] == []

    assert body["metadata"]["granularity"] == "month"
    assert body["metadata"]["date_start"] == "2020-01-01"
    assert body["metadata"]["date_end"] == "2020-03-31"

    data = body["national"]["data"]
    assert len(data) == 3
    assert data[0]["date"] == "2020-01-01"
    assert "tmin_mean" in data[0]
    assert "tmax_mean" in data[0]


@pytest.mark.usefixtures("fake_minmax_dep")
def test_station_filter_returns_station_series(client: APIClient):
    resp = client.get(
        URL,
        {
            "date_start": "2020-01-01",
            "date_end": "2020-03-31",
            "granularity": "month",
            "station_ids": "07149,07222",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert "national" not in body
    assert len(body["stations"]) == 2
    assert body["stations"][0]["station_id"] == "07149"
    assert body["stations"][1]["station_id"] == "07222"

    data = body["stations"][0]["data"]
    assert len(data) == 3
    assert "tmin_mean" in data[0]
    assert "tmax_mean" in data[0]


@pytest.mark.usefixtures("fake_minmax_dep")
@pytest.mark.parametrize("granularity", ["day", "month", "year"])
def test_all_granularities_return_200(client: APIClient, granularity: str):
    resp = client.get(
        URL,
        {
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "granularity": granularity,
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "national" in body
    assert body["metadata"]["granularity"] == granularity
