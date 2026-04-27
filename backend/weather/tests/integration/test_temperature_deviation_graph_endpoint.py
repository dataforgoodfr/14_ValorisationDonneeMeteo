import pytest
from rest_framework.test import APIClient

from weather.bootstrap_temperature_deviation import (
    TemperatureDeviationDependencyProvider,
)
from weather.data_sources.temperature_deviation_fake import (
    FakeTemperatureDeviationDailyDataSource,
)


@pytest.fixture
def fake_temperature_deviation_dep():
    TemperatureDeviationDependencyProvider.set_builder(
        lambda: FakeTemperatureDeviationDailyDataSource()
    )
    try:
        yield
    finally:
        TemperatureDeviationDependencyProvider.reset()


@pytest.mark.usefixtures("fake_temperature_deviation_dep")
def test_get_temperature_deviation_graph_day_happy_path(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-01-03",
            "granularity": "day",
            "station_ids": "07149,07222",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"] == {
        "date_start": "2024-01-01",
        "date_end": "2024-01-03",
        "baseline": "1991-2020",
        "granularity": "day",
        "slice_type": "full",
    }

    assert "national" in body
    assert "stations" in body
    assert len(body["stations"]) == 2

    national = body["national"]
    s1 = body["stations"][0]
    s2 = body["stations"][1]

    assert len(national["data"]) == 3

    assert s1["station_id"] == "07149"
    assert s1["station_name"] == "Station 07149"
    assert len(s1["data"]) == 3

    assert s2["station_id"] == "07222"
    assert s2["station_name"] == "Station 07222"
    assert len(s2["data"]) == 3


@pytest.mark.usefixtures("fake_temperature_deviation_dep")
def test_get_temperature_deviation_graph_without_national(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-01-03",
            "granularity": "day",
            "include_national": "false",
            "station_ids": "07149",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert "national" not in body
    assert len(body["stations"]) == 1
    assert body["stations"][0]["station_id"] == "07149"


def test_get_temperature_deviation_graph_returns_400_if_include_national_false_and_no_station_ids(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-01-03",
            "granularity": "day",
            "include_national": "false",
        },
    )

    assert resp.status_code == 400
    body = resp.json()

    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "station_ids" in body["error"]["details"]


def test_get_temperature_deviation_graph_returns_400_if_date_start_gt_date_end(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2024-02-01",
            "date_end": "2024-01-03",
            "granularity": "day",
        },
    )

    assert resp.status_code == 400
    body = resp.json()

    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "date_end" in body["error"]["details"]


@pytest.mark.usefixtures("fake_temperature_deviation_dep")
def test_get_temperature_deviation_graph_endpoint_uses_dependency_provider(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-01-03",
            "granularity": "day",
            "station_ids": "07149",
            "include_national": "false",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["stations"][0]["station_id"] == "07149"
    assert "national" not in body


@pytest.mark.usefixtures("fake_temperature_deviation_dep")
def test_get_temperature_deviation_graph_year_month_of_year_slice_happy_path(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2020-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "month_of_year",
            "month_of_year": 2,
            "station_ids": "07149",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"] == {
        "date_start": "2020-01-01",
        "date_end": "2024-12-31",
        "baseline": "1991-2020",
        "granularity": "year",
        "slice_type": "month_of_year",
        "month_of_year": 2,
    }

    assert "national" in body
    assert "stations" in body
    assert len(body["stations"]) == 1
    assert body["stations"][0]["station_id"] == "07149"


@pytest.mark.usefixtures("fake_temperature_deviation_dep")
def test_get_temperature_deviation_graph_month_day_of_month_slice_happy_path(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-06-30",
            "granularity": "month",
            "slice_type": "day_of_month",
            "day_of_month": 31,
            "station_ids": "07149",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"] == {
        "date_start": "2024-01-01",
        "date_end": "2024-06-30",
        "baseline": "1991-2020",
        "granularity": "month",
        "slice_type": "day_of_month",
        "day_of_month": 31,
    }

    assert "national" in body
    assert "stations" in body
    assert len(body["stations"]) == 1


@pytest.mark.usefixtures("fake_temperature_deviation_dep")
def test_get_temperature_deviation_graph_year_day_of_month_slice_happy_path(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2020-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "day_of_month",
            "month_of_year": 2,
            "day_of_month": 29,
            "station_ids": "07149",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"] == {
        "date_start": "2020-01-01",
        "date_end": "2024-12-31",
        "baseline": "1991-2020",
        "granularity": "year",
        "slice_type": "day_of_month",
        "month_of_year": 2,
        "day_of_month": 29,
    }

    assert "national" in body
    assert "stations" in body
    assert len(body["stations"]) == 1


def test_get_temperature_deviation_graph_returns_400_for_day_granularity_with_day_of_month_slice(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "granularity": "day",
            "slice_type": "day_of_month",
            "day_of_month": 15,
        },
    )

    assert resp.status_code == 400
    body = resp.json()

    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "slice_type" in body["error"]["details"]


def test_get_temperature_deviation_graph_returns_400_for_month_of_year_slice_without_month_of_year(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2020-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "month_of_year",
        },
    )

    assert resp.status_code == 400
    body = resp.json()

    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "month_of_year" in body["error"]["details"]


def test_get_temperature_deviation_graph_returns_400_for_year_day_of_month_slice_without_month_of_year(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/deviation/graph",
        {
            "date_start": "2020-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "day_of_month",
            "day_of_month": 15,
        },
    )

    assert resp.status_code == 400
    body = resp.json()

    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "month_of_year" in body["error"]["details"]
