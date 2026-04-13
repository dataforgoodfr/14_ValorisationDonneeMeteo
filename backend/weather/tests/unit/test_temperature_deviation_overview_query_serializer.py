import datetime as dt

from weather.serializers import TemperatureDeviationOverviewQuerySerializer


def test_temperature_deviation_overview_query_serializer_happy_path():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "station_ids": "07149,07255",
            "station_search": "Montsouris",
            "temperature_mean_min": 10.0,
            "temperature_mean_max": 20.0,
            "deviation_min": -1.5,
            "deviation_max": 3.5,
            "ordering": "station_name",
            "offset": 25,
            "limit": 25,
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["date_start"] == dt.date(2025, 3, 1)
    assert s.validated_data["date_end"] == dt.date(2025, 3, 31)
    assert s.validated_data["station_search"] == "Montsouris"
    assert s.validated_data["temperature_mean_min"] == 10.0
    assert s.validated_data["temperature_mean_max"] == 20.0
    assert s.validated_data["deviation_min"] == -1.5
    assert s.validated_data["deviation_max"] == 3.5
    assert s.validated_data["ordering"] == "station_name"
    assert s.validated_data["offset"] == 25
    assert s.validated_data["limit"] == 25
    assert s.validated_data["station_ids"] == ("07149", "07255")


def test_temperature_deviation_overview_query_serializer_defaults():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["station_search"] is None
    assert s.validated_data["temperature_mean_min"] is None
    assert s.validated_data["temperature_mean_max"] is None
    assert s.validated_data["deviation_min"] is None
    assert s.validated_data["deviation_max"] is None
    assert s.validated_data["ordering"] == "-deviation"
    assert s.validated_data["offset"] == 0
    assert s.validated_data["limit"] == 50
    assert s.validated_data["station_ids"] == ()


def test_temperature_deviation_overview_query_serializer_rejects_date_start_gt_date_end():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-04-01",
            "date_end": "2025-03-31",
        }
    )

    assert not s.is_valid()
    assert "date_end" in s.errors


def test_temperature_deviation_overview_query_serializer_rejects_temperature_bounds():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "temperature_mean_min": 20.0,
            "temperature_mean_max": 10.0,
        }
    )

    assert not s.is_valid()
    assert "temperature_mean_max" in s.errors


def test_temperature_deviation_overview_query_serializer_rejects_deviation_bounds():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "deviation_min": 3.0,
            "deviation_max": -1.0,
        }
    )

    assert not s.is_valid()
    assert "deviation_max" in s.errors


def test_temperature_deviation_overview_query_serializer_blank_station_search_is_none():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "station_search": "",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["station_search"] is None


def test_temperature_deviation_overview_query_serializer_whitespace_station_search_is_none():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "station_search": "   ",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["station_search"] is None


def test_temperature_deviation_overview_query_serializer_parses_departments_regions_and_alt():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "departments": "13,75",
            "regions": "Occitanie,Île-de-France",
            "alt_min": 100,
            "alt_max": 500,
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["departments"] == ("13", "75")
    assert s.validated_data["regions"] == ("Occitanie", "Île-de-France")
    assert s.validated_data["alt_min"] == 100.0
    assert s.validated_data["alt_max"] == 500.0


def test_temperature_deviation_overview_query_serializer_rejects_alt_bounds():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "alt_min": 500,
            "alt_max": 100,
        }
    )

    assert not s.is_valid()
    assert "alt_max" in s.errors


def test_temperature_deviation_overview_query_serializer_rejects_negative_offset():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "offset": -1,
        }
    )

    assert not s.is_valid()
    assert "offset" in s.errors


def test_temperature_deviation_overview_query_serializer_rejects_limit_too_large():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "limit": 1000,
        }
    )

    assert not s.is_valid()
    assert "limit" in s.errors


def test_temperature_deviation_overview_query_serializer_parses_station_ids():
    s = TemperatureDeviationOverviewQuerySerializer(
        data={
            "date_start": "2025-03-01",
            "date_end": "2025-03-31",
            "station_ids": "07149,07255",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["station_ids"] == ("07149", "07255")


def test_temperature_deviation_overview_query_serializer_accepts_department_and_region_ordering():
    for ordering in ("department", "-department", "region", "-region"):
        s = TemperatureDeviationOverviewQuerySerializer(
            data={
                "date_start": "2025-03-01",
                "date_end": "2025-03-31",
                "ordering": ordering,
            }
        )

        assert s.is_valid(), s.errors
        assert s.validated_data["ordering"] == ordering
