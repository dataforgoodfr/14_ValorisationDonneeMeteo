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
    }

    assert len(body["stations"]) == 2


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
