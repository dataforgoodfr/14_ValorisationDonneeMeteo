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


# Stub qui retourne un point fixe pour n'importe quelle date
class AnyDateObservedDataSource(NationalIndicatorBaselineDataSource):
    def __init__(self, temperature: float):
        self._temperature = temperature

    def fetch_daily_series(self, query) -> list[ObservedPoint]:
        start, end = query.date_start, query.date_end
        return [
            ObservedPoint(
                date=start + dt.timedelta(days=i), temperature=self._temperature
            )
            for i in range((end - start).days + 1)
        ]


class AnyDateBaselineDataSource(NationalIndicatorBaselineDataSource):
    def __init__(self, mean: float, std_dev: float):
        self._baseline = _baseline(mean, std_dev)

    def fetch_daily_baseline(self, _day: dt.date) -> BaselinePoint:
        return self._baseline


# ─── Tests : pic chaud ────────────────────────────────────────────────────────


def test_hot_peak_detected_when_temperature_exceeds_upper_bound():
    observed = [ObservedPoint(date=dt.date(2024, 7, 15), temperature=25.0)]
    baselines = {(7, 15): _baseline(mean=20.0, std_dev=2.0)}  # upper = 22.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 15),
        date_end=dt.date(2024, 7, 15),
    )

    assert result.current.hot_peak_count == 1


def test_hot_peak_not_detected_when_temperature_below_upper_bound():
    observed = [ObservedPoint(date=dt.date(2024, 7, 15), temperature=21.0)]
    baselines = {(7, 15): _baseline(mean=20.0, std_dev=2.0)}  # upper = 22.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 15),
        date_end=dt.date(2024, 7, 15),
    )

    assert result.current.hot_peak_count == 0


def test_hot_peak_not_detected_when_temperature_equals_upper_bound():
    observed = [ObservedPoint(date=dt.date(2024, 7, 15), temperature=22.0)]
    baselines = {(7, 15): _baseline(mean=20.0, std_dev=2.0)}  # upper = 22.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 15),
        date_end=dt.date(2024, 7, 15),
    )

    assert result.current.hot_peak_count == 0


# ─── Tests : pic froid ────────────────────────────────────────────────────────


def test_cold_peak_detected_when_temperature_below_lower_bound():
    observed = [ObservedPoint(date=dt.date(2024, 1, 10), temperature=3.0)]
    baselines = {(1, 10): _baseline(mean=8.0, std_dev=2.0)}  # lower = 6.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 1, 10),
        date_end=dt.date(2024, 1, 10),
    )

    assert result.current.cold_peak_count == 1


def test_cold_peak_not_detected_when_temperature_above_lower_bound():
    observed = [ObservedPoint(date=dt.date(2024, 1, 10), temperature=7.0)]
    baselines = {(1, 10): _baseline(mean=8.0, std_dev=2.0)}  # lower = 6.0

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 1, 10),
        date_end=dt.date(2024, 1, 10),
    )

    assert result.current.cold_peak_count == 0


# ─── Tests : isolation hot / cold ─────────────────────────────────────────────


def test_cold_day_does_not_appear_in_hot_peak_count():
    observed = [ObservedPoint(date=dt.date(2024, 1, 10), temperature=3.0)]
    baselines = {(1, 10): _baseline(mean=8.0, std_dev=2.0)}  # lower=6, upper=10

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 1, 10),
        date_end=dt.date(2024, 1, 10),
    )

    assert result.current.hot_peak_count == 0
    assert result.current.cold_peak_count == 1


def test_hot_day_does_not_appear_in_cold_peak_count():
    observed = [ObservedPoint(date=dt.date(2024, 7, 15), temperature=25.0)]
    baselines = {(7, 15): _baseline(mean=20.0, std_dev=2.0)}  # lower=18, upper=22

    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource(observed),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 7, 15),
        date_end=dt.date(2024, 7, 15),
    )

    assert result.current.cold_peak_count == 0
    assert result.current.hot_peak_count == 1


def test_hot_and_cold_peaks_returned_simultaneously():
    result = get_national_indicator_kpi(
        observed_data_source=AnyDateObservedDataSource(temperature=25.0),
        baseline_data_source=AnyDateBaselineDataSource(mean=20.0, std_dev=2.0),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 1),
    )
    assert result.current.hot_peak_count == 1

    result2 = get_national_indicator_kpi(
        observed_data_source=AnyDateObservedDataSource(temperature=15.0),
        baseline_data_source=AnyDateBaselineDataSource(mean=20.0, std_dev=2.0),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 1),
    )
    assert result2.current.cold_peak_count == 1


# ─── Tests : période précédente ───────────────────────────────────────────────


def test_previous_period_dates_are_correct():
    # current : 2024-01-10 → 2024-01-14 (5 jours)
    # previous : 2024-01-05 → 2024-01-09 (5 jours)
    calls: list[tuple[dt.date, dt.date]] = []

    class TrackingObservedDataSource(NationalIndicatorBaselineDataSource):
        def fetch_daily_series(self, query) -> list[ObservedPoint]:
            calls.append((query.date_start, query.date_end))
            return []

    result = get_national_indicator_kpi(
        observed_data_source=TrackingObservedDataSource(),
        baseline_data_source=AnyDateBaselineDataSource(mean=10.0, std_dev=2.0),
        date_start=dt.date(2024, 1, 10),
        date_end=dt.date(2024, 1, 14),
    )

    assert calls[0] == (dt.date(2024, 1, 10), dt.date(2024, 1, 14))
    assert calls[1] == (dt.date(2024, 1, 5), dt.date(2024, 1, 9))
    assert result.current.itn_mean is None
    assert result.previous.itn_mean is None


def test_previous_period_computes_independent_stats():
    # current (2024-01-10) : température 25 → pic chaud
    # previous (2024-01-09) : température 5 → pic froid
    baselines = {
        (1, 10): _baseline(mean=10.0, std_dev=2.0),
        (1, 9): _baseline(mean=10.0, std_dev=2.0),
    }

    class TwoDayObserved(NationalIndicatorBaselineDataSource):
        def fetch_daily_series(self, query) -> list[ObservedPoint]:
            temps = {dt.date(2024, 1, 10): 25.0, dt.date(2024, 1, 9): 5.0}
            start, end = query.date_start, query.date_end
            return [
                ObservedPoint(
                    date=start + dt.timedelta(days=i),
                    temperature=temps.get(start + dt.timedelta(days=i), 10.0),
                )
                for i in range((end - start).days + 1)
            ]

    result = get_national_indicator_kpi(
        observed_data_source=TwoDayObserved(),
        baseline_data_source=StubBaselineDataSource(baselines),
        date_start=dt.date(2024, 1, 10),
        date_end=dt.date(2024, 1, 10),
    )

    assert result.current.hot_peak_count == 1
    assert result.current.cold_peak_count == 0
    assert result.previous.cold_peak_count == 1
    assert result.previous.hot_peak_count == 0


# ─── Tests : plusieurs jours ──────────────────────────────────────────────────


def test_only_peak_days_counted_over_multiple_days():
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
    )

    assert result.current.hot_peak_count == 2


def test_empty_observed_series_returns_zero_counts():
    result = get_national_indicator_kpi(
        observed_data_source=AnyDateObservedDataSource(temperature=10.0),
        baseline_data_source=AnyDateBaselineDataSource(mean=10.0, std_dev=2.0),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 1),
    )

    assert result.current.hot_peak_count == 0
    assert result.current.cold_peak_count == 0


# ─── Tests : days_above_baseline / days_below_baseline ───────────────────────


def test_days_above_baseline_counts_days_with_positive_deviation():
    result = get_national_indicator_kpi(
        observed_data_source=AnyDateObservedDataSource(temperature=21.0),
        baseline_data_source=AnyDateBaselineDataSource(mean=20.0, std_dev=2.0),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 1),
    )
    assert result.current.days_above_baseline == 1
    assert result.current.days_below_baseline == 0


def test_days_below_baseline_counts_days_with_negative_deviation():
    result = get_national_indicator_kpi(
        observed_data_source=AnyDateObservedDataSource(temperature=19.0),
        baseline_data_source=AnyDateBaselineDataSource(mean=20.0, std_dev=2.0),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 1),
    )
    assert result.current.days_above_baseline == 0
    assert result.current.days_below_baseline == 1


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
    )

    assert result.current.itn_mean == 20.0


def test_itn_mean_is_none_when_observed_series_is_empty():
    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource([]),
        baseline_data_source=StubBaselineDataSource({}),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 3),
    )

    assert result.current.itn_mean is None


# ─── Tests : deviation_from_normal ────────────────────────────────────────────


def test_deviation_from_normal_positive_when_warmer_than_baseline():
    result = get_national_indicator_kpi(
        observed_data_source=AnyDateObservedDataSource(temperature=23.0),
        baseline_data_source=AnyDateBaselineDataSource(mean=20.0, std_dev=2.0),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 2),
    )
    assert result.current.deviation_from_normal == pytest.approx(3.0)


def test_deviation_from_normal_negative_when_colder_than_baseline():
    result = get_national_indicator_kpi(
        observed_data_source=AnyDateObservedDataSource(temperature=6.0),
        baseline_data_source=AnyDateBaselineDataSource(mean=10.0, std_dev=2.0),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
    )
    assert result.current.deviation_from_normal == pytest.approx(-4.0)


def test_deviation_from_normal_is_none_when_observed_series_is_empty():
    result = get_national_indicator_kpi(
        observed_data_source=StubObservedDataSource([]),
        baseline_data_source=StubBaselineDataSource({}),
        date_start=dt.date(2024, 7, 1),
        date_end=dt.date(2024, 7, 3),
    )

    assert result.current.deviation_from_normal is None
