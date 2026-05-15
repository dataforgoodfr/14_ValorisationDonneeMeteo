"""
Tests d'intégration pour TimescaleNationalIndicatorKpiDataSource.

Chaque test sème :
  - mv_itn_daily_all_years (ITN journalier observé) via insert_itn_daily
  - v_itn_baseline_daily_1991_2020 (baseline 1991-2020) via insert_daily_baseline

… puis appelle compute_kpi(...) et vérifie la sortie.
"""

from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import TimescaleNationalIndicatorKpiDataSource
from weather.tests.helpers.itn import insert_itn_daily
from weather.tests.helpers.itn_baseline import insert_daily_baseline

pytestmark = pytest.mark.django_db


def _ds() -> TimescaleNationalIndicatorKpiDataSource:
    return TimescaleNationalIndicatorKpiDataSource()


def _single_day(date: dt.date) -> dict:
    """Périodes pour un test qui ne porte que sur la période courante."""
    return {
        "current_start": date,
        "current_end": date,
        "previous_start": date - dt.timedelta(days=1),
        "previous_end": date - dt.timedelta(days=1),
    }


# ─── Hot peak ────────────────────────────────────────────────────────────────


def test_hot_peak_detected_when_temperature_exceeds_upper_bound() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=15, itn=25.0)
    insert_daily_baseline(month=7, day=15, mean=20.0, std=2.0)  # upper = 22.0

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.current.hot_peak_count == 1


def test_hot_peak_not_detected_when_temperature_below_upper_bound() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=15, itn=21.0)
    insert_daily_baseline(month=7, day=15, mean=20.0, std=2.0)  # upper = 22.0

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.current.hot_peak_count == 0


def test_hot_peak_not_detected_when_temperature_equals_upper_bound() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=15, itn=22.0)
    insert_daily_baseline(month=7, day=15, mean=20.0, std=2.0)  # upper = 22.0

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.current.hot_peak_count == 0


# ─── Cold peak ───────────────────────────────────────────────────────────────


def test_cold_peak_detected_when_temperature_below_lower_bound() -> None:
    insert_itn_daily(year=2024, month=1, day_of_month=10, itn=3.0)
    insert_daily_baseline(month=1, day=10, mean=8.0, std=2.0)  # lower = 6.0

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 1, 10)))

    assert result.current.cold_peak_count == 1


def test_cold_peak_not_detected_when_temperature_above_lower_bound() -> None:
    insert_itn_daily(year=2024, month=1, day_of_month=10, itn=7.0)
    insert_daily_baseline(month=1, day=10, mean=8.0, std=2.0)  # lower = 6.0

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 1, 10)))

    assert result.current.cold_peak_count == 0


# ─── Isolation hot / cold ────────────────────────────────────────────────────


def test_cold_day_does_not_appear_in_hot_peak_count() -> None:
    insert_itn_daily(year=2024, month=1, day_of_month=10, itn=3.0)
    insert_daily_baseline(month=1, day=10, mean=8.0, std=2.0)  # lower=6, upper=10

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 1, 10)))

    assert result.current.hot_peak_count == 0
    assert result.current.cold_peak_count == 1


def test_hot_day_does_not_appear_in_cold_peak_count() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=15, itn=25.0)
    insert_daily_baseline(month=7, day=15, mean=20.0, std=2.0)  # lower=18, upper=22

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.current.hot_peak_count == 1
    assert result.current.cold_peak_count == 0


# ─── Previous period ─────────────────────────────────────────────────────────


def test_previous_period_computes_independent_stats() -> None:
    # current (2024-01-10) : ITN 25 → pic chaud
    insert_itn_daily(year=2024, month=1, day_of_month=10, itn=25.0)
    insert_daily_baseline(month=1, day=10, mean=10.0, std=2.0)
    # previous (2024-01-09) : ITN 5 → pic froid
    insert_itn_daily(year=2024, month=1, day_of_month=9, itn=5.0)
    insert_daily_baseline(month=1, day=9, mean=10.0, std=2.0)

    result = _ds().compute_kpi(
        current_start=dt.date(2024, 1, 10),
        current_end=dt.date(2024, 1, 10),
        previous_start=dt.date(2024, 1, 9),
        previous_end=dt.date(2024, 1, 9),
    )

    assert result.current.hot_peak_count == 1
    assert result.current.cold_peak_count == 0
    assert result.previous.hot_peak_count == 0
    assert result.previous.cold_peak_count == 1


def test_empty_previous_period_returns_zero_counts_and_none_mean() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=15, itn=25.0)
    insert_daily_baseline(month=7, day=15, mean=20.0, std=2.0)
    # rien dans la période précédente

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.previous.hot_peak_count == 0
    assert result.previous.cold_peak_count == 0
    assert result.previous.days_above_baseline == 0
    assert result.previous.days_below_baseline == 0
    assert result.previous.itn_mean is None
    assert result.previous.deviation_from_normal is None


# ─── Plusieurs jours ─────────────────────────────────────────────────────────


def test_only_peak_days_counted_over_multiple_days() -> None:
    # upper = 22.0
    insert_itn_daily(year=2024, month=7, day_of_month=1, itn=23.0)  # pic
    insert_itn_daily(year=2024, month=7, day_of_month=2, itn=21.0)  # normal
    insert_itn_daily(year=2024, month=7, day_of_month=3, itn=25.0)  # pic
    for d in (1, 2, 3):
        insert_daily_baseline(month=7, day=d, mean=20.0, std=2.0)

    result = _ds().compute_kpi(
        current_start=dt.date(2024, 7, 1),
        current_end=dt.date(2024, 7, 3),
        previous_start=dt.date(2024, 6, 28),
        previous_end=dt.date(2024, 6, 30),
    )

    assert result.current.hot_peak_count == 2


def test_empty_observed_series_returns_zero_counts() -> None:
    # rien à insérer

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.current.hot_peak_count == 0
    assert result.current.cold_peak_count == 0


# ─── days_above_baseline / days_below_baseline ──────────────────────────────


def test_days_above_baseline_counts_days_with_positive_deviation() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=1, itn=21.0)
    insert_daily_baseline(month=7, day=1, mean=20.0, std=2.0)

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 1)))

    assert result.current.days_above_baseline == 1
    assert result.current.days_below_baseline == 0


def test_days_below_baseline_counts_days_with_negative_deviation() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=1, itn=19.0)
    insert_daily_baseline(month=7, day=1, mean=20.0, std=2.0)

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 1)))

    assert result.current.days_above_baseline == 0
    assert result.current.days_below_baseline == 1


def test_day_equal_to_baseline_counts_neither_above_nor_below() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=1, itn=20.0)
    insert_daily_baseline(month=7, day=1, mean=20.0, std=2.0)

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 1)))

    assert result.current.days_above_baseline == 0
    assert result.current.days_below_baseline == 0


# ─── itn_mean ────────────────────────────────────────────────────────────────


def test_itn_mean_is_average_of_all_observed_days() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=1, itn=10.0)
    insert_itn_daily(year=2024, month=7, day_of_month=2, itn=20.0)
    insert_itn_daily(year=2024, month=7, day_of_month=3, itn=30.0)
    for d in (1, 2, 3):
        insert_daily_baseline(month=7, day=d, mean=20.0, std=2.0)

    result = _ds().compute_kpi(
        current_start=dt.date(2024, 7, 1),
        current_end=dt.date(2024, 7, 3),
        previous_start=dt.date(2024, 6, 28),
        previous_end=dt.date(2024, 6, 30),
    )

    assert result.current.itn_mean == 20.0


def test_itn_mean_is_none_when_observed_series_is_empty() -> None:
    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.current.itn_mean is None


# ─── deviation_from_normal ──────────────────────────────────────────────────


def test_deviation_from_normal_positive_when_warmer_than_baseline() -> None:
    insert_itn_daily(year=2024, month=7, day_of_month=1, itn=23.0)
    insert_itn_daily(year=2024, month=7, day_of_month=2, itn=23.0)
    insert_daily_baseline(month=7, day=1, mean=20.0, std=2.0)
    insert_daily_baseline(month=7, day=2, mean=20.0, std=2.0)

    result = _ds().compute_kpi(
        current_start=dt.date(2024, 7, 1),
        current_end=dt.date(2024, 7, 2),
        previous_start=dt.date(2024, 6, 29),
        previous_end=dt.date(2024, 6, 30),
    )

    assert result.current.deviation_from_normal == pytest.approx(3.0)


def test_deviation_from_normal_negative_when_colder_than_baseline() -> None:
    insert_itn_daily(year=2024, month=1, day_of_month=1, itn=6.0)
    insert_itn_daily(year=2024, month=1, day_of_month=2, itn=6.0)
    insert_daily_baseline(month=1, day=1, mean=10.0, std=2.0)
    insert_daily_baseline(month=1, day=2, mean=10.0, std=2.0)

    result = _ds().compute_kpi(
        current_start=dt.date(2024, 1, 1),
        current_end=dt.date(2024, 1, 2),
        previous_start=dt.date(2023, 12, 30),
        previous_end=dt.date(2023, 12, 31),
    )

    assert result.current.deviation_from_normal == pytest.approx(-4.0)


def test_deviation_from_normal_is_none_when_observed_series_is_empty() -> None:
    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.current.deviation_from_normal is None


# ─── Couverture : observé sans baseline → ignoré ────────────────────────────


def test_observed_day_without_baseline_is_skipped() -> None:
    # ITN observé pour 2024-07-15 mais PAS de baseline pour (7, 15)
    insert_itn_daily(year=2024, month=7, day_of_month=15, itn=25.0)

    result = _ds().compute_kpi(**_single_day(dt.date(2024, 7, 15)))

    assert result.current.hot_peak_count == 0
    assert result.current.itn_mean is None
