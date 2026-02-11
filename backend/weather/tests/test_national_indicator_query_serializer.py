import pytest

from weather.serializers import NationalIndicatorQuerySerializer


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
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": date_start,
            "date_end": date_end,
            "granularity": "month",
        }
    )

    ok = s.is_valid()
    assert ok is should_be_valid

    if not should_be_valid:
        assert "date_end" in s.errors


def test_granularity_must_be_valid_choice():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-31",
            "granularity": "hour",  # invalide
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "granularity" in s.errors


def test_granularity_day_rejects_non_full_slice_type():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-07",
            "granularity": "day",
            "slice_type": "day_of_month",  # interdit
            "day_of_month": 1,
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "slice_type" in s.errors


def test_granularity_day_defaults_slice_type_to_full():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-07",
            "granularity": "day",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["slice_type"] == "full"


def test_granularity_day_forbids_month_of_year():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-07",
            "granularity": "day",
            "month_of_year": 1,
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "month_of_year" in s.errors


def test_granularity_day_forbids_day_of_month():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-01-07",
            "granularity": "day",
            "day_of_month": 1,
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "day_of_month" in s.errors


def test_slice_type_full_forbids_month_of_year():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            "granularity": "month",
            "slice_type": "full",
            "month_of_year": 1,
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "month_of_year" in s.errors


def test_slice_type_full_forbids_day_of_month():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            "granularity": "month",
            "slice_type": "full",
            "day_of_month": 1,
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "day_of_month" in s.errors


@pytest.mark.parametrize("invalid_granularity", ["month", "day"])
def test_slice_type_month_of_year_requires_granularity_year(invalid_granularity):
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": invalid_granularity,  # interdit
            "slice_type": "month_of_year",
            "month_of_year": 1,
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "slice_type" in s.errors


def test_slice_type_month_of_year_requires_month_of_year():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "month_of_year",
            # month_of_year absent
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "month_of_year" in s.errors


def test_slice_type_month_of_year_forbids_day_of_month():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "month_of_year",
            "month_of_year": 1,
            "day_of_month": 1,  # interdit
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "day_of_month" in s.errors


def test_slice_type_day_of_month_requires_day_of_month():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            "granularity": "month",
            "slice_type": "day_of_month",
            # day_of_month absent
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "day_of_month" in s.errors


def test_day_of_month_with_granularity_year_requires_month_of_year():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "day_of_month",
            "day_of_month": 1,
            # month_of_year absent
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "month_of_year" in s.errors


def test_day_of_month_with_granularity_month_forbids_month_of_year():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            "granularity": "month",
            "slice_type": "day_of_month",
            "day_of_month": 1,
            "month_of_year": 1,  # interdit
        }
    )

    ok = s.is_valid()
    assert not ok
    assert "month_of_year" in s.errors


def test_valid_month_full_defaults():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            "granularity": "month",
        }
    )

    assert s.is_valid(), s.errors
    assert s.validated_data["slice_type"] == "full"


def test_valid_month_day_of_month():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2024-01-01",
            "date_end": "2024-03-31",
            "granularity": "month",
            "slice_type": "day_of_month",
            "day_of_month": 31,
        }
    )

    assert s.is_valid(), s.errors


def test_valid_year_month_of_year():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "month_of_year",
            "month_of_year": 1,
        }
    )

    assert s.is_valid(), s.errors


def test_valid_year_specific_day_of_year():
    s = NationalIndicatorQuerySerializer(
        data={
            "date_start": "2020-01-01",
            "date_end": "2024-12-31",
            "granularity": "year",
            "slice_type": "day_of_month",
            "month_of_year": 1,
            "day_of_month": 1,
        }
    )

    assert s.is_valid(), s.errors
