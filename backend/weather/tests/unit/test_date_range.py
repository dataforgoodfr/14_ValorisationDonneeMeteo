import datetime as dt

import pytest

from weather.utils.date_range import (
    clamp_day_to_month_end,
    days_in_month_in_range,
    iter_days_intersecting,
    iter_month_starts_intersecting,
    iter_year_starts_intersecting,
    monthly_points_in_range,
    yearly_points_in_range,
)


def test_iter_days_intersecting_inclusive_single_day():
    out = list(iter_days_intersecting(dt.date(2024, 1, 1), dt.date(2024, 1, 1)))
    assert out == [dt.date(2024, 1, 1)]


def test_iter_days_intersecting_inclusive_range():
    out = list(iter_days_intersecting(dt.date(2024, 1, 1), dt.date(2024, 1, 3)))
    assert out == [dt.date(2024, 1, 1), dt.date(2024, 1, 2), dt.date(2024, 1, 3)]


@pytest.mark.parametrize(
    "year,month,day,expected",
    [
        (2024, 1, 31, 31),
        (2024, 4, 31, 30),  # avril
        (2024, 2, 31, 29),  # bissextile
        (2023, 2, 31, 28),  # non bissextile
        (2024, 2, 29, 29),
        (2023, 2, 28, 28),
    ],
)
def test_clamp_day_to_month_end(year, month, day, expected):
    assert clamp_day_to_month_end(year, month, day) == expected


def test_iter_month_starts_intersecting_mid_month_to_mid_month():
    # 2024-01-15..2024-03-10 => Jan, Feb, Mar
    out = list(
        iter_month_starts_intersecting(dt.date(2024, 1, 15), dt.date(2024, 3, 10))
    )
    assert out == [dt.date(2024, 1, 1), dt.date(2024, 2, 1), dt.date(2024, 3, 1)]


def test_iter_month_starts_intersecting_cross_year():
    out = list(
        iter_month_starts_intersecting(dt.date(2023, 12, 31), dt.date(2024, 1, 1))
    )
    assert out == [dt.date(2023, 12, 1), dt.date(2024, 1, 1)]


def test_iter_year_starts_intersecting_includes_both_ends():
    out = list(iter_year_starts_intersecting(dt.date(2024, 6, 1), dt.date(2026, 2, 1)))
    assert out == [dt.date(2024, 1, 1), dt.date(2025, 1, 1), dt.date(2026, 1, 1)]


def test_days_in_month_in_range_filters_only_selected_month_and_is_inclusive():
    out = days_in_month_in_range(
        date_start=dt.date(2024, 1, 30),
        date_end=dt.date(2024, 2, 2),
        month=2,
    )
    assert out == (dt.date(2024, 2, 1), dt.date(2024, 2, 2))


def test_days_in_month_in_range_can_be_empty():
    out = days_in_month_in_range(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 31),
        month=2,
    )
    assert out == ()


def test_monthly_points_in_range_clamps_and_filters_by_window():
    # day_of_month=31 => Feb clamp to 29 (bissextile)
    out = monthly_points_in_range(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 3, 31),
        day_of_month=31,
    )
    assert out == (dt.date(2024, 1, 31), dt.date(2024, 2, 29), dt.date(2024, 3, 31))


def test_monthly_points_in_range_excludes_candidates_outside_window():
    # window 2024-01-15..2024-03-10, target day=1 => Jan 1 excluded, Feb 1 ok, Mar 1 ok
    out = monthly_points_in_range(
        date_start=dt.date(2024, 1, 15),
        date_end=dt.date(2024, 3, 10),
        day_of_month=1,
    )
    assert out == (dt.date(2024, 2, 1), dt.date(2024, 3, 1))


def test_yearly_points_in_range_clamps_and_filters_by_window():
    out = yearly_points_in_range(
        date_start=dt.date(2021, 1, 1),
        date_end=dt.date(2023, 12, 31),
        month=2,
        day_of_month=31,
    )
    assert out == (dt.date(2021, 2, 28), dt.date(2022, 2, 28), dt.date(2023, 2, 28))


def test_yearly_points_in_range_excludes_candidates_outside_window():
    out = yearly_points_in_range(
        date_start=dt.date(2024, 6, 1),
        date_end=dt.date(2026, 2, 1),
        month=1,
        day_of_month=1,
    )
    # 2024-01-01 exclu (avant start), 2025-01-01 ok, 2026-01-01 ok (<= end)
    assert out == (dt.date(2025, 1, 1), dt.date(2026, 1, 1))
