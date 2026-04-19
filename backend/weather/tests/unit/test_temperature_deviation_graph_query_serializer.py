import datetime as dt

from weather.serializers import TemperatureDeviationGraphQuerySerializer


def test_temperature_deviation_query_serializer_happy_path():
    s = TemperatureDeviationGraphQuerySerializer(
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
    assert s.validated_data["slice_type"] == "full"


def test_temperature_deviation_query_serializer_include_national_defaults_true():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "granularity": "month",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["include_national"] is True
    assert s.validated_data.get("station_ids", ()) == ()
    assert s.validated_data["slice_type"] == "full"


def test_temperature_deviation_query_serializer_rejects_date_start_gt_date_end():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-02-01",
            "date_end": "2024-01-31",
            "granularity": "day",
        }
    )

    assert not s.is_valid()
    assert "date_end" in s.errors


def test_temperature_deviation_query_serializer_requires_station_ids_if_include_national_false():
    s = TemperatureDeviationGraphQuerySerializer(
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
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "granularity": "day",
            "station_ids": "",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["station_ids"] == ()


def test_temperature_deviation_query_serializer_accepts_year_month_of_year_slice():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "month_of_year",
            "month_of_year": 2,
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["slice_type"] == "month_of_year"
    assert s.validated_data["month_of_year"] == 2


def test_temperature_deviation_query_serializer_accepts_year_day_of_month_slice():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "day_of_month",
            "month_of_year": 2,
            "day_of_month": 29,
        }
    )

    assert s.is_valid(), s.errors


def test_temperature_deviation_query_serializer_accepts_month_day_of_month_slice():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-06-30",
            "granularity": "month",
            "slice_type": "day_of_month",
            "day_of_month": 31,
        }
    )

    assert s.is_valid(), s.errors


def test_temperature_deviation_query_serializer_rejects_day_granularity_with_month_of_year_slice():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-10",
            "granularity": "day",
            "slice_type": "month_of_year",
            "month_of_year": 2,
        }
    )

    assert not s.is_valid()
    assert "slice_type" in s.errors


def test_temperature_deviation_query_serializer_rejects_day_granularity_with_day_of_month_slice():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-10",
            "granularity": "day",
            "slice_type": "day_of_month",
            "day_of_month": 15,
        }
    )

    assert not s.is_valid()
    assert "slice_type" in s.errors


def test_temperature_deviation_query_serializer_rejects_day_granularity_with_month_of_year_param():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-10",
            "granularity": "day",
            "month_of_year": 2,
        }
    )

    assert not s.is_valid()
    assert "month_of_year" in s.errors


def test_temperature_deviation_query_serializer_rejects_day_granularity_with_day_of_month_param():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-10",
            "granularity": "day",
            "day_of_month": 15,
        }
    )

    assert not s.is_valid()
    assert "day_of_month" in s.errors


def test_temperature_deviation_query_serializer_rejects_month_of_year_when_slice_type_full():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "full",
            "month_of_year": 2,
        }
    )

    assert not s.is_valid()
    assert "month_of_year" in s.errors


def test_temperature_deviation_query_serializer_rejects_day_of_month_when_slice_type_full():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "full",
            "day_of_month": 15,
        }
    )

    assert not s.is_valid()
    assert "day_of_month" in s.errors


def test_temperature_deviation_query_serializer_rejects_month_of_year_slice_for_month_granularity():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "month",
            "slice_type": "month_of_year",
            "month_of_year": 2,
        }
    )

    assert not s.is_valid()
    assert "slice_type" in s.errors


def test_temperature_deviation_query_serializer_rejects_month_of_year_slice_without_month_of_year():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "month_of_year",
        }
    )

    assert not s.is_valid()
    assert "month_of_year" in s.errors


def test_temperature_deviation_query_serializer_rejects_day_of_month_with_month_of_year_slice():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "month_of_year",
            "month_of_year": 2,
            "day_of_month": 15,
        }
    )

    assert not s.is_valid()
    assert "day_of_month" in s.errors


def test_temperature_deviation_query_serializer_rejects_year_day_of_month_slice_without_month_of_year():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "day_of_month",
            "day_of_month": 15,
        }
    )

    assert not s.is_valid()
    assert "month_of_year" in s.errors


def test_temperature_deviation_query_serializer_rejects_month_day_of_month_slice_with_month_of_year():
    s = TemperatureDeviationGraphQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-06-30",
            "granularity": "month",
            "slice_type": "day_of_month",
            "day_of_month": 15,
            "month_of_year": 2,
        }
    )

    assert not s.is_valid()
    assert "month_of_year" in s.errors
