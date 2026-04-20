import datetime as dt

import pytest

from weather.services.national_indicator.kpi_use_case import get_national_indicator_kpi
from weather.services.national_indicator.protocols import (
    NationalIndicatorBaselineDataSource,
)
from weather.services.national_indicator.types import (
    BaselinePoint,
    ObservedPoint,
)


class StubObservedDataSource(NationalIndicatorBaselineDataSource):
    def __init__(self, points: list[ObservedPoint]):
        self._points = points

    def fetch_daily_series(self, _query) -> list[ObservedPoint]:
        return self._points


class StubBaselineDataSource(NationalIndicatorBaselineDataSource):
    def __init__(self, baselines: dict[tuple[int, int], BaselinePoint]):
        # clé = (month, day_of_month)
        self._baselines = baselines

    def fetch_daily_baseline(self, day: dt.date) -> BaselinePoint:
        return self._baselines[(day.month, day.day)]


def _baseline(mean: float, std_dev: float) -> BaselinePoint:
    return BaselinePoint(
        baseline_mean=mean,
        baseline_std_dev_upper=mean + std_dev,
        baseline_std_dev_lower=mean - std_dev,
        baseline_max=0.0,
        baseline_min=0.0,
    )


# ─── Tests : pic chaud ────────────────────────────────────────────────────────


def test_hot_peak_detected_when_temperature_exceeds_upper_bound():
    observed = [ObservedPoint(date=dt.date(2024, 7, 15), temperature=25.0)]
    baselines = {(7, 15): _baseline(mean=20.0, std_dev=2.0)}  # upper = 22.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 15),
        date_end=dt.date(2024, 7, 15),
        peak_type="hot",
    )

    assert result.count == 1
    assert result.days[0].date == dt.date(2024, 7, 15)
    assert result.days[0].temperature == 25.0
    assert result.days[0].baseline_mean == 20.0
    assert result.days[0].baseline_std_dev == 2.0


def test_hot_peak_not_detected_when_temperature_below_upper_bound():
    observed = [ObservedPoint(date=dt.date(2024, 7, 15), temperature=21.0)]
    baselines = {(7, 15): _baseline(mean=20.0, std_dev=2.0)}  # upper = 22.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 15),
        date_end=dt.date(2024, 7, 15),
        peak_type="hot",
    )

    assert result.count == 0
    assert result.days == []


def test_hot_peak_not_detected_when_temperature_equals_upper_bound():
    observed = [ObservedPoint(date=dt.date(2024, 7, 15), temperature=22.0)]
    baselines = {(7, 15): _baseline(mean=20.0, std_dev=2.0)}  # upper = 22.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 15),
        date_end=dt.date(2024, 7, 15),
        peak_type="hot",
    )

    assert result.count == 0


# ─── Tests : pic froid ────────────────────────────────────────────────────────


def test_cold_peak_detected_when_temperature_below_lower_bound():
    observed = [ObservedPoint(date=dt.date(2024, 1, 10), temperature=3.0)]
    baselines = {(1, 10): _baseline(mean=8.0, std_dev=2.0)}  # lower = 6.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 1, 10),
        date_end=dt.date(2024, 1, 10),
        peak_type="cold",
    )

    assert result.count == 1
    assert result.days[0].date == dt.date(2024, 1, 10)
    assert result.days[0].temperature == 3.0
    assert result.days[0].baseline_mean == 8.0
    assert result.days[0].baseline_std_dev == 2.0


def test_cold_peak_not_detected_when_temperature_above_lower_bound():
    observed = [ObservedPoint(date=dt.date(2024, 1, 10), temperature=7.0)]
    baselines = {(1, 10): _baseline(mean=8.0, std_dev=2.0)}  # lower = 6.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 1, 10),
        date_end=dt.date(2024, 1, 10),
        peak_type="cold",
    )

    assert result.count == 0
    assert result.days == []


# ─── Tests : plusieurs jours ──────────────────────────────────────────────────


def test_only_peak_days_returned_over_multiple_days():
    observed = [
        ObservedPoint(date=dt.date(2024, 7, 1), temperature=23.0),  # pic (upper=22)
        ObservedPoint(date=dt.date(2024, 7, 2), temperature=21.0),  # normal
        ObservedPoint(date=dt.date(2024, 7, 3), temperature=25.0),  # pic (upper=22)
    ]
    baseline = _baseline(mean=20.0, std_dev=2.0)
    baselines = {(7, 1): baseline, (7, 2): baseline, (7, 3): baseline}

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 3),
        peak_type="hot",
    )

    assert result.count == 2
    assert [d.date for d in result.days] == [dt.date(2024, 7, 1), dt.date(2024, 7, 3)]


def test_empty_observed_series_returns_empty_result():
    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource([]),
        baseline_data_source=StubBaselineDataSource({}),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 3),
        peak_type="hot",
    )

    assert result.count == 0
    assert result.days == []


def test_hot_type_does_not_return_cold_days():
    observed = [ObservedPoint(date=dt.date(2024, 1, 10), temperature=3.0)]
    baselines = {(1, 10): _baseline(mean=8.0, std_dev=2.0)}  # lower=6, upper=10

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 1, 10),
        date_end=dt.date(2024, 1, 10),
        peak_type="hot",
    )

    assert result.count == 0


# ─── Tests : itn_mean ─────────────────────────────────────────────────────────


def test_itn_mean_is_average_of_all_observed_days():
    observed = [
        ObservedPoint(date=dt.date(2024, 7, 1), temperature=10.0),
        ObservedPoint(date=dt.date(2024, 7, 2), temperature=20.0),
        ObservedPoint(date=dt.date(2024, 7, 3), temperature=30.0),
    ]
    baseline = _baseline(mean=20.0, std_dev=2.0)
    baselines = {(7, 1): baseline, (7, 2): baseline, (7, 3): baseline}

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 3),
        peak_type="hot",
    )

    assert result.itn_mean == 20.0


def test_itn_mean_includes_non_peak_days():
    # Seul le 3 juillet est un pic, mais la moyenne porte sur les 3 jours
    observed = [
        ObservedPoint(date=dt.date(2024, 7, 1), temperature=10.0),
        ObservedPoint(date=dt.date(2024, 7, 2), temperature=10.0),
        ObservedPoint(date=dt.date(2024, 7, 3), temperature=25.0),  # pic
    ]
    baseline = _baseline(mean=20.0, std_dev=2.0)
    baselines = {(7, 1): baseline, (7, 2): baseline, (7, 3): baseline}

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 3),
        peak_type="hot",
    )

    assert result.count == 1
    assert result.itn_mean == pytest.approx((10.0 + 10.0 + 25.0) / 3)


def test_itn_mean_is_none_when_observed_series_is_empty():
    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource([]),
        baseline_data_source=StubBaselineDataSource({}),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 3),
        peak_type="hot",
    )

    assert result.itn_mean is None


def test_itn_mean_with_single_day():
    observed = [ObservedPoint(date=dt.date(2024, 7, 1), temperature=15.5)]
    baselines = {(7, 1): _baseline(mean=20.0, std_dev=2.0)}

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 1),
        peak_type="hot",
    )

    assert result.itn_mean == 15.5


# ─── Tests : deviation_from_normal ────────────────────────────────────────────


def test_deviation_from_normal_positive_when_warmer_than_baseline():
    observed = [
        ObservedPoint(date=dt.date(2024, 7, 1), temperature=22.0),
        ObservedPoint(date=dt.date(2024, 7, 2), temperature=24.0),
    ]
    # baseline_mean = 20.0 pour les deux jours
    baseline = _baseline(mean=20.0, std_dev=2.0)
    baselines = {(7, 1): baseline, (7, 2): baseline}

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 2),
        peak_type="hot",
    )

    # itn_mean = 23.0, baseline_period_mean = 20.0
    assert result.deviation_from_normal == pytest.approx(3.0)


def test_deviation_from_normal_negative_when_colder_than_baseline():
    observed = [
        ObservedPoint(date=dt.date(2024, 1, 1), temperature=5.0),
        ObservedPoint(date=dt.date(2024, 1, 2), temperature=7.0),
    ]
    baseline = _baseline(mean=10.0, std_dev=2.0)
    baselines = {(1, 1): baseline, (1, 2): baseline}

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        peak_type="cold",
    )

    # itn_mean = 6.0, baseline_period_mean = 10.0
    assert result.deviation_from_normal == pytest.approx(-4.0)


def test_deviation_from_normal_uses_per_day_baseline_mean():
    # Baselines différentes par jour pour vérifier que la moyenne porte sur tous les jours
    observed = [
        ObservedPoint(date=dt.date(2024, 7, 1), temperature=20.0),
        ObservedPoint(date=dt.date(2024, 7, 2), temperature=20.0),
    ]
    baselines = {
        (7, 1): _baseline(mean=10.0, std_dev=2.0),
        (7, 2): _baseline(mean=30.0, std_dev=2.0),
    }

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 2),
        peak_type="hot",
    )

    # itn_mean = 20.0, baseline_period_mean = (10 + 30) / 2 = 20.0
    assert result.deviation_from_normal == pytest.approx(0.0)


def test_deviation_from_normal_is_none_when_observed_series_is_empty():
    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource([]),
        baseline_data_source=StubBaselineDataSource({}),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 3),
        peak_type="hot",
    )

    assert result.deviation_from_normal is None


# ─── Tests : peak_type facultatif ─────────────────────────────────────────────


def test_no_peak_type_returns_empty_days_and_zero_count():
    observed = [
        ObservedPoint(date=dt.date(2024, 7, 1), temperature=25.0),
        ObservedPoint(date=dt.date(2024, 7, 2), temperature=5.0),
    ]
    baseline = _baseline(mean=15.0, std_dev=2.0)
    baselines = {(7, 1): baseline, (7, 2): baseline}

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 2),
        peak_type=None,
    )

    assert result.count == 0
    assert result.days == []


def test_no_peak_type_still_computes_itn_mean_and_deviation():
    observed = [
        ObservedPoint(date=dt.date(2024, 7, 1), temperature=20.0),
        ObservedPoint(date=dt.date(2024, 7, 2), temperature=30.0),
    ]
    baseline = _baseline(mean=10.0, std_dev=2.0)
    baselines = {(7, 1): baseline, (7, 2): baseline}

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 2),
        peak_type=None,
    )

    assert result.itn_mean == 25.0
    assert result.deviation_from_normal == pytest.approx(15.0)
