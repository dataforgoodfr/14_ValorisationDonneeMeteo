import datetime as dt

from weather.serializers import TemperatureDeviationQuerySerializer


def test_temperature_deviation_query_serializer_happy_path():
    s = TemperatureDeviationQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "granularity": "day",
            "station_ids": "07149,07222",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["date_start"] == dt.date(2024, 1, 1)
    assert s.validated_data["date_end"] == dt.date(2024, 1, 31)
    assert s.validated_data["granularity"] == "day"
    assert s.validated_data["station_ids"] == ("07149", "07222")
    assert s.validated_data["include_national"] is True


def test_temperature_deviation_query_serializer_include_national_defaults_true():
    s = TemperatureDeviationQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "granularity": "month",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["include_national"] is True
    assert s.validated_data.get("station_ids", ()) == ()


def test_temperature_deviation_query_serializer_rejects_date_start_gt_date_end():
    s = TemperatureDeviationQuerySerializer(
        data={
            "date_start": "2024-02-01",
            "date_end": "2024-01-31",
            "granularity": "day",
        }
    )

    assert not s.is_valid()
    assert "date_end" in s.errors


def test_temperature_deviation_query_serializer_requires_station_ids_if_include_national_false():
    s = TemperatureDeviationQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "granularity": "day",
            "include_national": False,
        }
    )

    assert not s.is_valid()
    assert "station_ids" in s.errors


def test_temperature_deviation_query_serializer_empty_station_ids_are_empty_tuple():
    s = TemperatureDeviationQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "granularity": "day",
            "station_ids": "",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["station_ids"] == ()
