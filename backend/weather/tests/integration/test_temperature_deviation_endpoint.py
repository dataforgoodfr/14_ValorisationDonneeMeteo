def test_get_temperature_deviation_day_happy_path(client):
    resp = client.get(
        "/api/v1/temperature/deviation",
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
    }

    assert len(body["series"]) == 3

    national = body["series"][0]
    s1 = body["series"][1]
    s2 = body["series"][2]

    assert national["is_national"] is True
    assert "station_id" not in national
    assert len(national["data"]) == 3

    assert s1["is_national"] is False
    assert s1["station_id"] == "07149"
    assert s1["station_name"] == "Station 07149"
    assert len(s1["data"]) == 3

    assert s2["is_national"] is False
    assert s2["station_id"] == "07222"
    assert s2["station_name"] == "Station 07222"
    assert len(s2["data"]) == 3


def test_get_temperature_deviation_without_national(client):
    resp = client.get(
        "/api/v1/temperature/deviation",
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

    assert len(body["series"]) == 1
    assert body["series"][0]["is_national"] is False
    assert body["series"][0]["station_id"] == "07149"


def test_get_temperature_deviation_returns_400_if_include_national_false_and_no_station_ids(
    client,
):
    resp = client.get(
        "/api/v1/temperature/deviation",
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


def test_get_temperature_deviation_returns_400_if_date_start_gt_date_end(client):
    resp = client.get(
        "/api/v1/temperature/deviation",
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
