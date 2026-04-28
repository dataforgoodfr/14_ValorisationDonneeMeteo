from weather.serializers import RecordsGraphQuerySerializer


def test_records_graph_query_serializer_happy_path():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
        }
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["granularity"] == "year"
    assert s.validated_data["period_type"] == "all_time"
    assert s.validated_data["type_records"] == "all"
    assert s.validated_data["territoire"] == "france"


def test_records_graph_query_serializer_month_period_happy_path():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "month",
            "period_type": "month",
            "month": 7,
        }
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["month"] == 7


def test_records_graph_query_serializer_season_period_happy_path():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "period_type": "season",
            "season": "summer",
        }
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["season"] == "summer"


def test_records_graph_query_serializer_rejects_missing_date_start():
    s = RecordsGraphQuerySerializer(
        data={"date_end": "2025-12-31", "granularity": "year"}
    )
    assert not s.is_valid()
    assert "date_start" in s.errors


def test_records_graph_query_serializer_rejects_missing_date_end():
    s = RecordsGraphQuerySerializer(
        data={"date_start": "2020-01-01", "granularity": "year"}
    )
    assert not s.is_valid()
    assert "date_end" in s.errors


def test_records_graph_query_serializer_rejects_missing_granularity():
    s = RecordsGraphQuerySerializer(
        data={"date_start": "2020-01-01", "date_end": "2025-12-31"}
    )
    assert not s.is_valid()
    assert "granularity" in s.errors


def test_records_graph_query_serializer_rejects_unknown_granularity():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "week",
        }
    )
    assert not s.is_valid()
    assert "granularity" in s.errors


def test_records_graph_query_serializer_rejects_period_type_month_without_month():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "period_type": "month",
        }
    )
    assert not s.is_valid()
    assert "month" in s.errors


def test_records_graph_query_serializer_rejects_period_type_season_without_season():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "period_type": "season",
        }
    )
    assert not s.is_valid()
    assert "season" in s.errors


def test_records_graph_query_serializer_rejects_month_out_of_range():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "month",
            "period_type": "month",
            "month": 13,
        }
    )
    assert not s.is_valid()
    assert "month" in s.errors


def test_records_graph_query_serializer_rejects_unknown_season():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "period_type": "season",
            "season": "monsoon",
        }
    )
    assert not s.is_valid()
    assert "season" in s.errors


def test_records_graph_query_serializer_rejects_territoire_non_france_without_id():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "territoire": "department",
        }
    )
    assert not s.is_valid()
    assert "territoire_id" in s.errors


def test_records_graph_query_serializer_territoire_department_with_id_valid():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "territoire": "department",
            "territoire_id": "13",
        }
    )
    assert s.is_valid(), s.errors
    assert s.validated_data["territoire"] == "department"
    assert s.validated_data["territoire_id"] == "13"


def test_records_graph_query_serializer_rejects_unknown_type_records():
    s = RecordsGraphQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2025-12-31",
            "granularity": "year",
            "type_records": "warm",
        }
    )
    assert not s.is_valid()
    assert "type_records" in s.errors
