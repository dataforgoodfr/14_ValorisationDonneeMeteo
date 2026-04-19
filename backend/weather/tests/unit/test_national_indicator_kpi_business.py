import datetime as dt

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
