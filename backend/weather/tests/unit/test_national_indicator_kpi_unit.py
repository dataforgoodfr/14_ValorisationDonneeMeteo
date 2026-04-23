from weather.services.national_indicator.kpi_use_case import is_peak
from weather.services.national_indicator.types import BaselinePoint


def _baseline(mean: float, std_dev: float) -> BaselinePoint:
    return BaselinePoint(
        baseline_mean=mean,
        baseline_std_dev_upper=mean + std_dev,
        baseline_std_dev_lower=mean - std_dev,
        baseline_max=0.0,
        baseline_min=0.0,
    )


# ─── Pic chaud ────────────────────────────────────────────────────────────────


def test_is_peak_hot_true_when_above_upper_bound():
    assert is_peak(23.0, _baseline(mean=20.0, std_dev=2.0), "hot") is True


def test_is_peak_hot_false_when_below_upper_bound():
    assert is_peak(21.0, _baseline(mean=20.0, std_dev=2.0), "hot") is False


def test_is_peak_hot_false_when_equal_to_upper_bound():
    assert is_peak(22.0, _baseline(mean=20.0, std_dev=2.0), "hot") is False


# ─── Pic froid ────────────────────────────────────────────────────────────────


def test_is_peak_cold_true_when_below_lower_bound():
    assert is_peak(5.0, _baseline(mean=8.0, std_dev=2.0), "cold") is True


def test_is_peak_cold_false_when_above_lower_bound():
    assert is_peak(7.0, _baseline(mean=8.0, std_dev=2.0), "cold") is False


def test_is_peak_cold_false_when_equal_to_lower_bound():
    assert is_peak(6.0, _baseline(mean=8.0, std_dev=2.0), "cold") is False


# ─── Symétrie ─────────────────────────────────────────────────────────────────


def test_is_peak_hot_does_not_trigger_on_cold_day():
    assert is_peak(5.0, _baseline(mean=8.0, std_dev=2.0), "hot") is False


def test_is_peak_cold_does_not_trigger_on_hot_day():
    assert is_peak(23.0, _baseline(mean=20.0, std_dev=2.0), "cold") is False
