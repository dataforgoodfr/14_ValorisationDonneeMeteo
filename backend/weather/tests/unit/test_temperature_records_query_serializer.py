import datetime as dt

from weather.serializers import TemperatureRecordsQuerySerializer


def test_temperature_records_query_serializer_happy_path():
    s = TemperatureRecordsQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "station_ids": "12345678,87654321",
            "record_kind": "historical",
            "record_scope": "monthly",
            "type_records": "hot",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["date_start"] == dt.date(2024, 1, 1)
    assert s.validated_data["date_end"] == dt.date(2024, 12, 31)
    assert s.validated_data["station_ids"] == ("12345678", "87654321")
    assert s.validated_data["record_kind"] == "historical"
    assert s.validated_data["record_scope"] == "monthly"
    assert s.validated_data["type_records"] == "hot"


def test_temperature_records_query_serializer_rejects_date_start_gt_date_end():
    s = TemperatureRecordsQuerySerializer(
        data={
            "date_start": "2024-02-01",
            "date_end": "2024-01-31",
        }
    )

    assert not s.is_valid()
    assert "date_end" in s.errors


def test_temperature_records_query_serializer_parses_departments():
    s = TemperatureRecordsQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "departments": "13,75",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["departments"] == ("13", "75")


def test_temperature_records_query_serializer_allows_missing_dates():
    s = TemperatureRecordsQuerySerializer(
        data={
            "record_kind": "absolute",
            "record_scope": "all_time",
            "type_records": "all",
        }
    )
    assert s.is_valid(), s.errors
    assert s.validated_data.get("date_start") is None
    assert s.validated_data.get("date_end") is None


def test_temperature_records_query_serializer_rejects_temperature_min_gt_temperature_max():
    s = TemperatureRecordsQuerySerializer(
        data={
            "temperature_min": 30,
            "temperature_max": 20,
        }
    )
    assert not s.is_valid()
    assert "temperature_max" in s.errors
