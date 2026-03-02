from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from weather.bootstrap_itn import ITNDependencyProvider
from weather.services.national_indicator.protocols import (
    NationalIndicatorDailyDataSource,
)
from weather.services.national_indicator.types import (
    DailyPoint,
    DailySeriesQuery,
)
from weather.utils.date_range import iter_days_intersecting

pytestmark = pytest.mark.django_db


def test_get_national_indicator_month_happy_path(client, seed_itn_day):
    class InMemoryITNDependency(NationalIndicatorDailyDataSource):
        def fetch_daily_series(
            self,
            query: DailySeriesQuery,
        ) -> list[DailyPoint]:
            if query.target_dates is not None:
                days = query.target_dates
            else:
                days = iter_days_intersecting(query.date_start, query.date_end)

            out = []

            for d in days:
                out.append(
                    DailyPoint(
                        date=d,
                        temperature=10.0,
                        baseline_mean=9.0,
                        baseline_std_dev_upper=11.0,
                        baseline_std_dev_lower=7.0,
                        baseline_max=15.0,
                        baseline_min=5.0,
                    )
                )

            return out

    ITNDependencyProvider.set_builder(InMemoryITNDependency)

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

    expected_itn_month = 10

    # compute_national_indicator arrondit à 2 décimales
    assert ts[0]["temperature"] == round(expected_itn_month, 2)


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
