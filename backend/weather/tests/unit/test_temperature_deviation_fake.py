import datetime as dt

from weather.data_sources.temperature_deviation_fake import (
    FakeTemperatureDeviationDailyDataSource,
)
from weather.services.temperature_deviation.types import DailyDeviationSeriesQuery


def test_fake_temperature_deviation_national_returns_one_point_per_day():
    ds = FakeTemperatureDeviationDailyDataSource()
    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 3),
        station_ids=(),
        include_national=True,
    )

    out = ds.fetch_national_observed_series(query)

    assert len(out) == 3
    assert [p.date for p in out] == [
        dt.date(2024, 1, 1),
        dt.date(2024, 1, 2),
        dt.date(2024, 1, 3),
    ]


def test_fake_temperature_deviation_station_returns_requested_series():
    ds = FakeTemperatureDeviationDailyDataSource()
    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        station_ids=("07149", "07222"),
        include_national=False,
    )

    out = ds.fetch_stations_daily_series(query)

    assert len(out) == 2
    assert [s.station_id for s in out] == ["07149", "07222"]
    assert [s.station_name for s in out] == ["Station 07149", "Station 07222"]
    assert all(len(s.points) == 2 for s in out)


def test_fake_temperature_deviation_is_deterministic_for_same_query():
    ds = FakeTemperatureDeviationDailyDataSource()
    query = DailyDeviationSeriesQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 3),
        station_ids=("07149",),
        include_national=True,
    )

    nat_1 = ds.fetch_national_observed_series(query)
    nat_2 = ds.fetch_national_observed_series(query)

    st_1 = ds.fetch_stations_daily_series(query)
    st_2 = ds.fetch_stations_daily_series(query)

    assert nat_1 == nat_2
    assert st_1 == st_2


def test_fake_temperature_deviation_daily_baseline_returns_366_days():
    ds = FakeTemperatureDeviationDailyDataSource()

    out = ds.fetch_national_daily_baseline()

    assert len(out) == 366
    assert all(1 <= p.month <= 12 for p in out)
    assert all(1 <= p.day_of_month <= 31 for p in out)


def test_fake_temperature_deviation_monthly_baseline_returns_12_months():
    ds = FakeTemperatureDeviationDailyDataSource()

    out = ds.fetch_national_monthly_baseline()

    assert len(out) == 12
    assert [p.month for p in out] == list(range(1, 13))


def test_fake_temperature_deviation_yearly_baseline_returns_value():
    ds = FakeTemperatureDeviationDailyDataSource()

    out = ds.fetch_national_yearly_baseline()

    assert out is not None
    assert isinstance(out.mean, float)
