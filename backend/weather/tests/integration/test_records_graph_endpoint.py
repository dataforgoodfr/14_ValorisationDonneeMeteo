import pytest
from rest_framework.test import APIClient

from weather.bootstrap_records_graph import RecordsGraphDependencyProvider
from weather.data_sources.records_graph_fake import FakeRecordsGraphDataSource


@pytest.fixture
def fake_records_graph_dep():
    RecordsGraphDependencyProvider.set_builder(lambda: FakeRecordsGraphDataSource())
    try:
        yield
    finally:
        RecordsGraphDependencyProvider.reset()


@pytest.mark.usefixtures("fake_records_graph_dep")
def test_graph_happy_path_year(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
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
    assert "nb_records_battus" in first
    assert isinstance(first["nb_records_battus"], int)


@pytest.mark.usefixtures("fake_records_graph_dep")
def test_graph_happy_path_month(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
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


@pytest.mark.usefixtures("fake_records_graph_dep")
def test_graph_returns_nonzero_for_known_record_dates(client: APIClient):
    # Le fake contient un record chaud le 2019-07-25 (ORLY et BOURGES)
    resp = client.get(
        "/api/v1/temperature/records/graph",
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
    assert july["nb_records_battus"] > 0


@pytest.mark.usefixtures("fake_records_graph_dep")
def test_graph_territoire_department(client: APIClient):
    # Département 94 = ORLY uniquement
    resp = client.get(
        "/api/v1/temperature/records/graph",
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
    total = sum(b["nb_records_battus"] for b in body["buckets"])
    assert total > 0


@pytest.mark.usefixtures("fake_records_graph_dep")
def test_graph_territoire_unknown_department_returns_zeros(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
        {
            "date_start": "2019-01-01",
            "date_end": "2019-12-31",
            "granularity": "year",
            "territoire": "department",
            "territoire_id": "99",
        },
    )

    assert resp.status_code == 200
    body = resp.json()
    assert all(b["nb_records_battus"] == 0 for b in body["buckets"])


def test_graph_missing_required_params(client: APIClient):
    resp = client.get("/api/v1/temperature/records/graph")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"


def test_graph_missing_granularity(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
        {"date_start": "2019-01-01", "date_end": "2019-12-31"},
    )
    assert resp.status_code == 400


def test_graph_invalid_granularity(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
        {"date_start": "2019-01-01", "date_end": "2019-12-31", "granularity": "week"},
    )
    assert resp.status_code == 400


def test_graph_territoire_without_id_returns_400(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
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


@pytest.mark.usefixtures("fake_records_graph_dep")
def test_graph_type_records_all(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
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
    # "all" doit agréger hot + cold → plus de records que hot seul
    total_all = sum(b["nb_records_battus"] for b in body["buckets"])
    resp_hot = client.get(
        "/api/v1/temperature/records/graph",
        {
            "date_start": "1940-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "type_records": "hot",
        },
    )
    total_hot = sum(b["nb_records_battus"] for b in resp_hot.json()["buckets"])
    assert total_all > total_hot


@pytest.mark.usefixtures("fake_records_graph_dep")
def test_graph_records_have_expected_fields(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
        {"date_start": "1940-01-01", "date_end": "2025-12-31", "granularity": "year"},
    )
    assert resp.status_code == 200
    records = resp.json()["records"]
    assert len(records) > 0
    for r in records:
        assert "date" in r
        assert "station_id" in r
        assert "station_name" in r
        assert "type_records" in r and r["type_records"] in ("hot", "cold")
        assert "valeur" in r


@pytest.mark.usefixtures("fake_records_graph_dep")
def test_graph_period_type_month_requires_month(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records/graph",
        {
            "date_start": "2019-01-01",
            "date_end": "2019-12-31",
            "granularity": "month",
            "period_type": "month",
        },
    )
    assert resp.status_code == 400
    body = resp.json()
    assert "month" in body["error"]["details"]
