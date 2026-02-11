from django.urls import reverse
from rest_framework.test import APIClient


def test_get_national_indicator_month_happy_path():
    client = APIClient()

    url = reverse("temperature-national-indicator")

    resp = client.get(
        url,
        {
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            "granularity": "month",
        },
    )

    assert resp.status_code == 200

    data = resp.json()

    assert "metadata" in data
    assert "time_series" in data

    assert data["metadata"]["granularity"] == "month"
    assert data["metadata"]["slice_type"] == "full"

    assert isinstance(data["time_series"], list)
    assert len(data["time_series"]) > 0


def test_get_national_indicator_missing_required_parameter_returns_400():
    client = APIClient()
    url = reverse("temperature-national-indicator")

    resp = client.get(
        url,
        {
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            # granularity manquant
        },
    )

    assert resp.status_code == 400

    data = resp.json()

    assert "error" in data
    assert data["error"]["code"] == "INVALID_PARAMETER"
    assert "granularity" in data["error"]["details"]


def test_get_national_indicator_invalid_combination_returns_400():
    client = APIClient()
    url = reverse("temperature-national-indicator")

    resp = client.get(
        url,
        {
            "date_start": "2024-01-01",
            "date_end": "2024-01-07",
            "granularity": "day",
            "slice_type": "day_of_month",
            "day_of_month": 1,
        },
    )

    assert resp.status_code == 400

    data = resp.json()

    assert "error" in data
    assert data["error"]["code"] == "INVALID_PARAMETER"
    assert "slice_type" in data["error"]["details"]
