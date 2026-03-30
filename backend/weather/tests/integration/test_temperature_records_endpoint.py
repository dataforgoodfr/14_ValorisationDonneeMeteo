from rest_framework.test import APIClient


def test_get_temperature_records_happy_path(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"]["date_start"] == "2024-01-01"
    assert body["metadata"]["date_end"] == "2024-12-31"
    assert "stations" in body
    assert len(body["stations"]) > 0

    station = body["stations"][0]
    assert "id" in station
    assert "name" in station
    assert "hot_records" in station
    assert "cold_records" in station


def test_get_temperature_records_defaults_are_applied(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"] == {
        "date_start": "2024-01-01",
        "date_end": "2024-12-31",
        "record_kind": "absolute",
        "record_scope": "all_time",
        "type_records": "all",
        "station_ids": [],
        "departments": [],
        "temperature_min": None,
        "temperature_max": None,
    }

    assert len(body["stations"]) == 3


def test_get_temperature_records_returns_400_if_date_start_gt_date_end(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "date_start": "2024-02-01",
            "date_end": "2024-01-31",
        },
    )

    assert resp.status_code == 400
    body = resp.json()

    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "date_end" in body["error"]["details"]


def test_get_temperature_records_returns_departments_in_metadata(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "departments": "07,13",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"]["departments"] == ["07", "13"]


def test_get_temperature_records_filters_by_departments(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "departments": "07",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert len(body["stations"]) > 0
    assert all(station["id"].startswith("07") for station in body["stations"])


def test_get_temperature_records_allows_missing_dates(client: APIClient):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "record_kind": "historical",
            "record_scope": "monthly",
            "type_records": "all",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"]["date_start"] is None
    assert body["metadata"]["date_end"] is None
    assert "stations" in body


def test_get_temperature_records_returns_temperature_filters_in_metadata(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "temperature_min": "25",
            "temperature_max": "35",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["metadata"]["temperature_min"] == 25.0
    assert body["metadata"]["temperature_max"] == 35.0


def test_get_temperature_records_returns_400_if_temperature_min_gt_temperature_max(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "temperature_min": "35",
            "temperature_max": "25",
        },
    )

    assert resp.status_code == 400
    body = resp.json()

    assert body["error"]["code"] == "INVALID_PARAMETER"
    assert "temperature_max" in body["error"]["details"]


def test_get_temperature_records_filters_records_by_temperature_interval(
    client: APIClient,
):
    resp = client.get(
        "/api/v1/temperature/records",
        {
            "record_kind": "historical",
            "record_scope": "monthly",
            "type_records": "all",
            "temperature_min": "10",
            "temperature_max": "30",
        },
    )

    assert resp.status_code == 200
    body = resp.json()

    for station in body["stations"]:
        for record in station["hot_records"]:
            assert 10.0 <= record["value"] <= 30.0
        for record in station["cold_records"]:
            assert 10.0 <= record["value"] <= 30.0
