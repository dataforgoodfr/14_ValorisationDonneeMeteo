import pytest

from weather.serializers import NationalIndicatorKpiQuerySerializer


@pytest.mark.parametrize(
    "date_start,date_end,should_be_valid",
    [
        ("2024-01-01", "2024-01-01", True),
        ("2024-01-01", "2024-01-02", True),
        ("2024-01-02", "2024-01-01", False),
    ],
)
def test_date_start_must_be_before_or_equal_date_end(
    date_start, date_end, should_be_valid
):
    s = NationalIndicatorKpiQuerySerializer(
        data={"date_start": date_start, "date_end": date_end, "type": "hot"}
    )

    ok = s.is_valid()
    assert ok is should_be_valid

    if not should_be_valid:
        assert "date_end" in s.errors


@pytest.mark.parametrize("peak_type", ["hot", "cold"])
def test_type_accepts_hot_and_cold(peak_type):
    s = NationalIndicatorKpiQuerySerializer(
        data={"date_start": "2024-01-01", "date_end": "2024-01-31", "type": peak_type}
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["type"] == peak_type


@pytest.mark.parametrize("invalid_type", ["warm", "hot_cold", "", "HOT"])
def test_type_rejects_invalid_values(invalid_type):
    s = NationalIndicatorKpiQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "type": invalid_type,
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "type" in s.errors


def test_missing_type_is_invalid():
    s = NationalIndicatorKpiQuerySerializer(
        data={"date_start": "2024-01-01", "date_end": "2024-01-31"}
    )

    ok = s.is_valid()
    assert not ok
    assert "type" in s.errors


def test_missing_date_start_is_invalid():
    s = NationalIndicatorKpiQuerySerializer(
        data={"date_end": "2024-01-31", "type": "hot"}
    )

    ok = s.is_valid()
    assert not ok
    assert "date_start" in s.errors


def test_missing_date_end_is_invalid():
    s = NationalIndicatorKpiQuerySerializer(
        data={"date_start": "2024-01-01", "type": "cold"}
    )

    ok = s.is_valid()
    assert not ok
    assert "date_end" in s.errors


def test_valid_data_passes():
    s = NationalIndicatorKpiQuerySerializer(
        data={"date_start": "2024-01-01", "date_end": "2024-12-31", "type": "cold"}
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["date_start"].isoformat() == "2024-01-01"
    assert s.validated_data["date_end"].isoformat() == "2024-12-31"
