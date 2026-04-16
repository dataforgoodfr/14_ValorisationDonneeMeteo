import pytest
from rest_framework.test import APIClient

URL = "/api/v1/temperature/minmax/graph"


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
    body = resp.json()
    assert body["error"]["code"] == "INVALID_PARAMETER"


@pytest.mark.parametrize("granularity", ["day", "month", "year"])
def test_returns_501_with_valid_params(client: APIClient, granularity: str):
    """
    TODO : la logique métier n'est pas encore branchée.
    Un appel valide doit retourner 501, pas 400 ni 500.
    Ce test sera mis quand le data source sera branché.
    """
    resp = client.get(
        URL,
        {
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "granularity": granularity,
        },
    )

    assert resp.status_code == 501
    body = resp.json()
    assert body["error"]["code"] == "NOT_IMPLEMENTED"


def test_returns_501_with_territoire_filters(client: APIClient):
    resp = client.get(
        URL,
        {
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "granularity": "month",
            "departments": "75,69",
            "station_ids": "07149",
        },
    )

    assert resp.status_code == 501
