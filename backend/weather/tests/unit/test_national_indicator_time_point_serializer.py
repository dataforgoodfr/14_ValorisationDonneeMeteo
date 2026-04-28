from __future__ import annotations

import datetime as dt

import pytest

from weather.serializers import NationalIndicatorTimePointSerializer


def _valid_base() -> dict:
    return {
        "date": dt.date(2025, 6, 1),
        "temperature": 15.5,
        "baseline_mean": 12.0,
        "baseline_std_dev_upper": 14.0,
        "baseline_std_dev_lower": 10.0,
        "baseline_max": 20.0,
        "baseline_min": 5.0,
        "is_hot_peak": True,
        "is_cold_peak": False,
    }


def test_serializer_is_valid_with_hot_peak():
    s = NationalIndicatorTimePointSerializer(data=_valid_base())
    assert s.is_valid(), s.errors
    assert s.validated_data["is_hot_peak"] is True
    assert s.validated_data["is_cold_peak"] is False


def test_serializer_is_valid_with_cold_peak():
    data = {**_valid_base(), "is_hot_peak": False, "is_cold_peak": True}
    s = NationalIndicatorTimePointSerializer(data=data)
    assert s.is_valid(), s.errors
    assert s.validated_data["is_hot_peak"] is False
    assert s.validated_data["is_cold_peak"] is True


def test_serializer_is_valid_with_no_peak():
    data = {**_valid_base(), "is_hot_peak": False, "is_cold_peak": False}
    s = NationalIndicatorTimePointSerializer(data=data)
    assert s.is_valid(), s.errors


@pytest.mark.parametrize("missing_field", ["is_hot_peak", "is_cold_peak"])
def test_serializer_requires_peak_flags(missing_field: str):
    data = {k: v for k, v in _valid_base().items() if k != missing_field}
    s = NationalIndicatorTimePointSerializer(data=data)
    assert not s.is_valid()
    assert missing_field in s.errors
