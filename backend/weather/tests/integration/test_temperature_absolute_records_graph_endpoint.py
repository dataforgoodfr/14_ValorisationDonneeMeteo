import datetime as dt

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from weather.bootstrap_temperature_absolute_records_graph import (
    TemperatureAbsoluteRecordsGraphDependencyProvider,
)
from weather.data_sources.records_graph_fake import FakeAbsoluteRecordsGraphDataSource
from weather.services.records_graph.types import (
    AbsoluteRecordsGraphBucket,
    AbsoluteRecordsGraphResult,
    RecordsGraphRecord,
)

ENDPOINT = reverse("temperature-records-absolute-graph")


def given_this_data(result: AbsoluteRecordsGraphResult) -> None:
    """Câble le fake pour retourner ce result quel que soit le request."""
    TemperatureAbsoluteRecordsGraphDependencyProvider.set_builder(
        lambda: FakeAbsoluteRecordsGraphDataSource(result)
    )


@pytest.fixture(autouse=True)
def _reset_absolute_dep():
    yield
    TemperatureAbsoluteRecordsGraphDependencyProvider.reset()


def test_graph_happy_path_year(client: APIClient):
    given_this_data(
        AbsoluteRecordsGraphResult(
            buckets=[
                AbsoluteRecordsGraphBucket(bucket=str(y), nb_records_absolus=0)
                for y in range(1940, 2026)
            ],
            records=[],
        )
    )

    resp = client.get(
        ENDPOINT,
        {
            "date_start": "1940-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "buckets" in body
    assert "records" in body
    assert len(body["buckets"]) == 2025 - 1940 + 1
    first = body["buckets"][0]
    assert first["bucket"] == "1940"
    assert first["nb_records_absolus"] == 0


def test_graph_happy_path_month(client: APIClient):
    given_this_data(
        AbsoluteRecordsGraphResult(
            buckets=[
                AbsoluteRecordsGraphBucket(bucket=f"2019-{m:02d}", nb_records_absolus=0)
                for m in range(1, 13)
            ],
            records=[],
        )
    )

    resp = client.get(
        ENDPOINT,
        {
            "date_start": "2019-01-01",
            "date_end": "2019-12-31",
            "granularity": "month",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["buckets"]) == 12
    assert body["buckets"][0]["bucket"] == "2019-01"
    assert body["buckets"][-1]["bucket"] == "2019-12"


def test_graph_passes_through_nonzero_bucket(client: APIClient):
    given_this_data(
        AbsoluteRecordsGraphResult(
            buckets=[
                AbsoluteRecordsGraphBucket(
                    bucket=f"2019-{m:02d}",
                    nb_records_absolus=2 if m == 7 else 0,
                )
                for m in range(1, 13)
            ],
            records=[],
        )
    )

    resp = client.get(
        ENDPOINT,
        {
            "date_start": "2019-01-01",
            "date_end": "2019-12-31",
            "granularity": "month",
            "type_records": "hot",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    july = next(b for b in body["buckets"] if b["bucket"] == "2019-07")
    assert july["nb_records_absolus"] == 2


def test_graph_territoire_department_accepts_param(client: APIClient):
    given_this_data(
        AbsoluteRecordsGraphResult(
            buckets=[AbsoluteRecordsGraphBucket(bucket="2019", nb_records_absolus=3)],
            records=[],
        )
    )

    resp = client.get(
        ENDPOINT,
        {
            "date_start": "1940-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "territoire": "department",
            "territoire_id": "94",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["buckets"][0]["nb_records_absolus"] == 3


def test_graph_type_records_all_accepts_param(client: APIClient):
    given_this_data(
        AbsoluteRecordsGraphResult(
            buckets=[AbsoluteRecordsGraphBucket(bucket="2019", nb_records_absolus=5)],
            records=[],
        )
    )

    resp = client.get(
        ENDPOINT,
        {
            "date_start": "1940-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "type_records": "all",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "buckets" in body
    assert "records" in body
    assert body["buckets"][0]["nb_records_absolus"] == 5


def test_graph_serializes_records_with_expected_fields(client: APIClient):
    given_this_data(
        AbsoluteRecordsGraphResult(
            buckets=[],
            records=[
                RecordsGraphRecord(
                    date=dt.date(2019, 7, 25),
                    station_id="94003001",
                    station_name="ORLY",
                    department="94",
                    type_records="hot",
                    valeur=42.0,
                ),
            ],
        )
    )

    resp = client.get(
        ENDPOINT,
        {
            "date_start": "1940-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
        },
    )

    assert resp.status_code == 200
    records = resp.json()["records"]
    assert len(records) == 1
    r = records[0]
    assert r["date"] == "2019-07-25"
    assert r["station_id"] == "94003001"
    assert r["station_name"] == "ORLY"
    assert r["type_records"] == "hot"
    assert r["valeur"] == 42.0


def test_graph_period_type_month_without_month_returns_200(client: APIClient):
    given_this_data(AbsoluteRecordsGraphResult(buckets=[], records=[]))

    resp = client.get(
        ENDPOINT,
        {
            "date_start": "2019-01-01",
            "date_end": "2019-12-31",
            "granularity": "month",
            "period_type": "month",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "buckets" in body
    assert "records" in body


def test_graph_period_type_season_without_season_returns_200(client: APIClient):
    given_this_data(AbsoluteRecordsGraphResult(buckets=[], records=[]))

    resp = client.get(
        ENDPOINT,
        {
            "date_start": "2019-01-01",
            "date_end": "2019-12-31",
            "granularity": "year",
            "period_type": "season",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert "buckets" in body
    assert "records" in body


def test_graph_missing_required_params(client: APIClient):
    resp = client.get(ENDPOINT)
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"


def test_graph_missing_granularity(client: APIClient):
    resp = client.get(
        ENDPOINT,
        {"date_start": "2019-01-01", "date_end": "2019-12-31"},
    )
    assert resp.status_code == 400


def test_graph_invalid_granularity(client: APIClient):
    resp = client.get(
        ENDPOINT,
        {"date_start": "2019-01-01", "date_end": "2019-12-31", "granularity": "week"},
    )
    assert resp.status_code == 400


def test_graph_territoire_without_id_returns_400(client: APIClient):
    resp = client.get(
        ENDPOINT,
        {
            "date_start": "2019-01-01",
            "date_end": "2019-12-31",
            "granularity": "year",
            "territoire": "department",
        },
    )
    assert resp.status_code == 400
    body = resp.json()
    assert "territoire_id" in body["error"]["details"]
