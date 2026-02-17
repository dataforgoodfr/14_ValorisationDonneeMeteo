import datetime as dt

from weather.data_generators.national_indicator_fake import (
    generate_fake_national_indicator,
)


def test_fake_generator_day_granularity_returns_all_days_inclusive():
    payload = generate_fake_national_indicator(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 7),
        granularity="day",
    )

    ts = payload["time_series"]
    assert len(ts) == 7

    assert ts[0]["date"] == "2024-01-01"
    assert ts[-1]["date"] == "2024-01-07"

    # Série contiguë jour par jour
    dates = [dt.date.fromisoformat(p["date"]) for p in ts]
    for prev, cur in zip(dates, dates[1:], strict=False):
        assert cur == prev + dt.timedelta(days=1)


def test_fake_generator_month_granularity_returns_one_point_per_month():
    payload = generate_fake_national_indicator(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 3, 31),
        granularity="month",
    )

    ts = payload["time_series"]

    assert len(ts) == 3

    expected_dates = ["2024-01-01", "2024-02-01", "2024-03-01"]
    actual_dates = [p["date"] for p in ts]

    assert actual_dates == expected_dates


def test_month_granularity_includes_month_if_interval_intersects():
    payload = generate_fake_national_indicator(
        date_start=dt.date(2024, 1, 15),
        date_end=dt.date(2024, 3, 10),
        granularity="month",
    )

    ts = payload["time_series"]
    dates = [p["date"] for p in ts]

    assert dates == [
        "2024-01-01",
        "2024-02-01",
        "2024-03-01",
    ]


def test_day_of_month_clamps_to_last_day_of_month():
    payload = generate_fake_national_indicator(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 3, 31),
        granularity="month",
        slice_type="day_of_month",
        day_of_month=31,
    )

    ts = payload["time_series"]
    dates = [p["date"] for p in ts]

    assert dates == [
        "2024-01-31",
        "2024-02-29",  # clamp (année bissextile)
        "2024-03-31",
    ]


def test_day_of_month_clamps_to_feb_28_on_non_leap_year():
    payload = generate_fake_national_indicator(
        date_start=dt.date(2023, 1, 1),
        date_end=dt.date(2023, 3, 31),
        granularity="month",
        slice_type="day_of_month",
        day_of_month=31,
    )

    ts = payload["time_series"]
    dates = [p["date"] for p in ts]

    assert dates == [
        "2023-01-31",
        "2023-02-28",  # clamp (non bissextile)
        "2023-03-31",
    ]


def test_fake_generator_year_granularity_includes_years_intersecting_interval():
    payload = generate_fake_national_indicator(
        date_start=dt.date(2024, 6, 1),
        date_end=dt.date(2026, 2, 1),
        granularity="year",
    )

    ts = payload["time_series"]
    dates = [p["date"] for p in ts]

    assert dates == [
        "2024-01-01",
        "2025-01-01",
        "2026-01-01",
    ]


def test_fake_generator_year_month_of_year_sets_date_to_first_day_of_selected_month():
    payload = generate_fake_national_indicator(
        date_start=dt.date(2020, 6, 1),
        date_end=dt.date(2022, 2, 1),
        granularity="year",
        slice_type="month_of_year",
        month_of_year=2,
    )

    ts = payload["time_series"]
    dates = [p["date"] for p in ts]

    assert dates == [
        "2020-02-01",
        "2021-02-01",
        "2022-02-01",
    ]


def test_fake_generator_year_day_of_month_clamps_within_selected_month():
    payload = generate_fake_national_indicator(
        date_start=dt.date(2021, 1, 1),
        date_end=dt.date(2023, 12, 31),
        granularity="year",
        slice_type="day_of_month",
        month_of_year=2,
        day_of_month=31,
    )

    ts = payload["time_series"]
    dates = [p["date"] for p in ts]

    assert dates == [
        "2021-02-28",
        "2022-02-28",
        "2023-02-28",
    ]
