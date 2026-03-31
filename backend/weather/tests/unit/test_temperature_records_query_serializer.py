from weather.serializers import TemperatureRecordsQuerySerializer


def test_records_query_serializer_defaults_to_all_time_hot():
    s = TemperatureRecordsQuerySerializer(data={})
    assert s.is_valid(), s.errors
    assert s.validated_data["period_type"] == "all_time"
    assert s.validated_data["type_records"] == "hot"


def test_records_query_serializer_month_happy_path():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "month", "month": 7, "type_records": "hot"}
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["month"] == 7


def test_records_query_serializer_season_happy_path():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "season", "season": "winter", "type_records": "cold"}
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["season"] == "winter"
    assert s.validated_data["type_records"] == "cold"


def test_records_query_serializer_all_time_happy_path():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "all_time", "type_records": "hot"}
    )
    assert s.is_valid(), s.errors


def test_records_query_serializer_rejects_month_missing_when_period_type_month():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "month", "type_records": "hot"}
    )
    assert not s.is_valid()
    assert "month" in s.errors


def test_records_query_serializer_rejects_season_missing_when_period_type_season():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "season", "type_records": "cold"}
    )
    assert not s.is_valid()
    assert "season" in s.errors


def test_records_query_serializer_rejects_unknown_period_type():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "weekly", "type_records": "hot"}
    )
    assert not s.is_valid()
    assert "period_type" in s.errors


def test_records_query_serializer_rejects_month_out_of_range():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "month", "month": 13, "type_records": "hot"}
    )
    assert not s.is_valid()
    assert "month" in s.errors


def test_records_query_serializer_rejects_unknown_season():
    s = TemperatureRecordsQuerySerializer(
        data={"period_type": "season", "season": "monsoon", "type_records": "cold"}
    )
    assert not s.is_valid()
    assert "season" in s.errors
