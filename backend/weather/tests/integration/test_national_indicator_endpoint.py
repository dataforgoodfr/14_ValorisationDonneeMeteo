from __future__ import annotations

import datetime as dt

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_get_national_indicator_month_happy_path(client, seed_itn_day):
    # 2 jours seedés en janvier
    d1 = dt.date(2025, 1, 1)
    d2 = dt.date(2025, 1, 2)

    seed_itn_day(d1, always_val=10.0, reims_val=20.0)  # ITN1
    seed_itn_day(d2, always_val=10.0, reims_val=40.0)  # ITN2

    url = reverse("temperature-national-indicator")
    resp = client.get(
        url,
        {
            "date_start": "2025-01-01",
            "date_end": "2025-01-31",
            "granularity": "month",
            "slice_type": "full",
        },
    )

    assert resp.status_code == 200
    payload = resp.json()

    assert payload["metadata"]["baseline"] == "1991-2020"
    assert payload["metadata"]["granularity"] == "month"
    assert payload["metadata"]["slice_type"] == "full"

    ts = payload["time_series"]
    assert len(ts) == 1

    itn1 = (29 * 10.0 + 20.0) / 30.0
    itn2 = (29 * 10.0 + 40.0) / 30.0
    expected_month = (itn1 + itn2) / 2

    # compute_national_indicator arrondit à 2 décimales
    assert ts[0]["temperature"] == round(expected_month, 2)


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
