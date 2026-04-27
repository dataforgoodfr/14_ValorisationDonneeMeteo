import datetime as dt

from weather.serializers import TemperatureMinMaxGraphQuerySerializer


def test_happy_path_minimal():
    s = TemperatureMinMaxGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "granularity": "month",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["date_start"] == dt.date(2020, 1, 1)
    assert s.validated_data["date_end"] == dt.date(2020, 12, 31)
    assert s.validated_data["granularity"] == "month"
    # Les filtres territoire absents sont normalisés en tuple vide
    assert s.validated_data["station_ids"] == ()
    assert s.validated_data["departments"] == ()
    assert s.validated_data["regions"] == ()


def test_happy_path_with_territoire_filters():
    s = TemperatureMinMaxGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "granularity": "year",
            "station_ids": "07149,07222",
            "departments": "75,69",
            "regions": "Île-de-France",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["station_ids"] == ("07149", "07222")
    assert s.validated_data["departments"] == ("75", "69")
    assert s.validated_data["regions"] == ("Île-de-France",)


def test_rejects_date_start_greater_than_date_end():
    """date_end doit être >= date_start."""
    s = TemperatureMinMaxGraphQuerySerializer(
        data={
            "date_start": "2020-12-31",
            "date_end": "2020-01-01",
            "granularity": "day",
        }
    )

    assert not s.is_valid()
    assert "date_end" in s.errors


def test_rejects_missing_date_start():
    s = TemperatureMinMaxGraphQuerySerializer(
        data={
            "date_end": "2020-12-31",
            "granularity": "day",
        }
    )

    assert not s.is_valid()
    assert "date_start" in s.errors


def test_rejects_missing_granularity():
    s = TemperatureMinMaxGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
        }
    )

    assert not s.is_valid()
    assert "granularity" in s.errors


def test_rejects_invalid_granularity():
    s = TemperatureMinMaxGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "granularity": "week",
        }
    )

    assert not s.is_valid()
    assert "granularity" in s.errors


def test_empty_station_ids_normalized_to_empty_tuple():
    s = TemperatureMinMaxGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2020-12-31",
            "granularity": "day",
            "station_ids": "",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["station_ids"] == ()


def test_same_date_start_and_date_end_is_valid():
    s = TemperatureMinMaxGraphQuerySerializer(
        data={
            "date_start": "2020-06-15",
            "date_end": "2020-06-15",
            "granularity": "day",
        }
    )

    assert s.is_valid(), s.errors
