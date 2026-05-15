import datetime as dt

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from weather.tests.helpers.stations import insert_station


@pytest.mark.django_db
def test_station_list_filters_by_first_temperature_year_max(client: APIClient) -> None:
    insert_station(
        "00000001", "Station 1959", first_temperature_date=dt.datetime(1959, 1, 1)
    )
    insert_station(
        "00000002", "Station 1960", first_temperature_date=dt.datetime(1960, 1, 1)
    )
    insert_station(
        "00000003", "Station 1975", first_temperature_date=dt.datetime(1975, 6, 1)
    )

    response = client.get(
        reverse("station-list"),
        {"first_temperature_year_max": 1960},
    )

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert [station["code"] for station in response.json()["results"]] == [
        "00000001",
        "00000002",
    ]


@pytest.mark.django_db
def test_station_records_list_uses_station_records_view(client: APIClient) -> None:
    current_year = dt.date.today().year

    insert_station(
        "00000011",
        "Station eligible",
        first_temperature_date=dt.datetime(current_year - 51, 1, 1),
    )
    insert_station(
        "00000012",
        "Station too recent",
        first_temperature_date=dt.datetime(current_year - 49, 1, 1),
    )

    response = client.get(reverse("station-records-list"))

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert [station["code"] for station in response.json()["results"]] == ["00000011"]


@pytest.mark.django_db
def test_station_records_detail_returns_404_for_station_outside_records_view(
    client: APIClient,
) -> None:
    current_year = dt.date.today().year

    insert_station(
        "00000021",
        "Station eligible",
        first_temperature_date=dt.datetime(current_year - 51, 1, 1),
    )
    insert_station(
        "00000022",
        "Station too recent",
        first_temperature_date=dt.datetime(current_year - 49, 1, 1),
    )

    eligible_response = client.get(reverse("station-records-detail", args=["00000021"]))
    missing_response = client.get(reverse("station-records-detail", args=["00000022"]))

    assert eligible_response.status_code == 200
    assert eligible_response.json()["code"] == "00000021"
    assert missing_response.status_code == 404


@pytest.mark.django_db
def test_station_deviation_list_uses_station_deviation_view(client: APIClient) -> None:
    insert_station(
        "00000031",
        "Station eligible",
        first_temperature_date=dt.datetime(1996, 12, 31),
        classe_recente=4,
    )
    insert_station(
        "00000032",
        "Station too recent",
        first_temperature_date=dt.datetime(1997, 1, 1),
        classe_recente=4,
    )
    insert_station(
        "00000033",
        "Station wrong class",
        first_temperature_date=dt.datetime(1996, 12, 31),
        classe_recente=5,
    )

    response = client.get(reverse("station-deviation-list"))

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert [station["code"] for station in response.json()["results"]] == ["00000031"]


@pytest.mark.django_db
def test_station_deviation_detail_returns_404_for_station_outside_deviation_view(
    client: APIClient,
) -> None:
    insert_station(
        "00000041",
        "Station eligible",
        first_temperature_date=dt.datetime(1996, 12, 31),
        classe_recente=4,
    )
    insert_station(
        "00000042",
        "Station wrong class",
        first_temperature_date=dt.datetime(1996, 12, 31),
        classe_recente=5,
    )

    eligible_response = client.get(
        reverse("station-deviation-detail", args=["00000041"])
    )
    missing_response = client.get(
        reverse("station-deviation-detail", args=["00000042"])
    )

    assert eligible_response.status_code == 200
    assert eligible_response.json()["code"] == "00000041"
    assert missing_response.status_code == 404
