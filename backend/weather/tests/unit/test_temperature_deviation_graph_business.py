import datetime as dt

from weather.data_sources.temperature_deviation_fake import (
    FakeTemperatureDeviationDailyDataSource,
)
from weather.services.temperature_deviation.types import (
    DailyBaselinePoint,
    DailyDeviationPoint,
    MonthlyBaselinePoint,
    ObservedPoint,
    StationDailySeries,
    YearlyBaselinePoint,
)
from weather.services.temperature_deviation.use_case import get_temperature_deviation


def test_temperature_deviation_graph_business_day_happy_path():
    ds = FakeTemperatureDeviationDailyDataSource()

    out = get_temperature_deviation(
        data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 3),
        granularity="day",
        station_ids=("07149",),
        include_national=True,
    )

    assert "national" in out
    assert "stations" in out

    national = out["national"]
    station = out["stations"][0]

    assert len(national["data"]) == 3

    assert station["station_id"] == "07149"
    assert station["station_name"] == "Station 07149"
    assert len(station["data"]) == 3


def test_temperature_deviation_graph__business_month_aggregates_to_one_point_per_month():
    ds = FakeTemperatureDeviationDailyDataSource()

    out = get_temperature_deviation(
        data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 2, 29),
        granularity="month",
        station_ids=("07149",),
        include_national=True,
    )

    national = out["national"]
    station = out["stations"][0]

    assert [p["date"] for p in national["data"]] == [
        dt.date(2024, 1, 1),
        dt.date(2024, 2, 1),
    ]
    assert [p["date"] for p in station["data"]] == [
        dt.date(2024, 1, 1),
        dt.date(2024, 2, 1),
    ]


def test_temperature_deviation_graph__business_without_national_returns_only_stations():
    ds = FakeTemperatureDeviationDailyDataSource()

    out = get_temperature_deviation(
        data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 3),
        granularity="day",
        station_ids=("07149", "07222"),
        include_national=False,
    )

    assert "national" not in out
    assert len(out["stations"]) == 2
    assert [s["station_id"] for s in out["stations"]] == ["07149", "07222"]


def test_temperature_deviation_graph__business_deviation_equals_temperature_minus_baseline_mean():
    ds = FakeTemperatureDeviationDailyDataSource()

    out = get_temperature_deviation(
        data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 1),
        granularity="day",
        station_ids=("07149",),
        include_national=True,
    )

    point = out["national"]["data"][0]
    expected = round(point["temperature"] - point["baseline_mean"], 2)
    assert point["deviation"] == expected

    for station in out["stations"]:
        point = station["data"][0]
        expected = round(point["temperature"] - point["baseline_mean"], 2)
        assert point["deviation"] == expected


def test_temperature_deviation_graph__business_returns_expected_payload_on_simple_input():
    class DeterministicTemperatureDeviationDataSource:
        def fetch_national_observed_series(self, query):
            return [
                ObservedPoint(
                    date=dt.date(2024, 1, 1),
                    temperature=10.0,
                ),
                ObservedPoint(
                    date=dt.date(2024, 1, 2),
                    temperature=12.0,
                ),
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(month=1, day_of_month=1, mean=8.0),
                DailyBaselinePoint(month=1, day_of_month=2, mean=9.0),
            ]

        def fetch_national_monthly_baseline(self):
            return [
                MonthlyBaselinePoint(month=1, mean=8.5),
            ]

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(mean=8.5)

        def fetch_stations_daily_series(self, query):
            return [
                StationDailySeries(
                    station_id="07149",
                    station_name="Station 07149",
                    points=[
                        DailyDeviationPoint(
                            date=dt.date(2024, 1, 1),
                            temperature=7.0,
                            baseline_mean=6.0,
                        ),
                        DailyDeviationPoint(
                            date=dt.date(2024, 1, 2),
                            temperature=9.0,
                            baseline_mean=8.5,
                        ),
                    ],
                )
            ]


def test_temperature_deviation_graph_business_national_month_partial_uses_daily_baseline():
    class DS:
        def fetch_national_observed_series(self, query):
            return [
                ObservedPoint(date=dt.date(2024, 1, 1), temperature=10.0),
                ObservedPoint(date=dt.date(2024, 1, 2), temperature=14.0),
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(month=1, day_of_month=1, mean=1.0),
                DailyBaselinePoint(month=1, day_of_month=2, mean=3.0),
            ]

        def fetch_national_monthly_baseline(self):
            return [
                MonthlyBaselinePoint(month=1, mean=20.0),
            ]

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(mean=999.0)

        def fetch_stations_daily_series(self, query):
            return []

    out = get_temperature_deviation(
        data_source=DS(),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        granularity="month",
        station_ids=(),
        include_national=True,
    )

    data = out["national"]["data"]

    assert len(data) == 1

    point = data[0]

    # moyenne observée : (10 + 14) / 2 = 12
    assert point["temperature"] == 12.0

    # bucket partiel → fallback daily : (1 + 3) / 2 = 2
    assert point["baseline_mean"] == 2.0

    # deviation = 12 - 2 = 10
    assert point["deviation"] == 10.0


def test_national_month_full_bucket_uses_monthly_baseline():
    class DS:
        def fetch_national_observed_series(self, query):
            # mois complet
            return [
                ObservedPoint(date=dt.date(2024, 1, d), temperature=10.0)
                for d in range(1, 32)
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(month=1, day_of_month=d, mean=1.0)
                for d in range(1, 32)
            ]

        def fetch_national_monthly_baseline(self):
            return [MonthlyBaselinePoint(month=1, mean=20.0)]

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(mean=999.0)

        def fetch_stations_daily_series(self, query):
            return []

    out = get_temperature_deviation(
        data_source=DS(),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 31),
        granularity="month",
        station_ids=(),
        include_national=True,
    )

    point = out["national"]["data"][0]

    assert point["baseline_mean"] == 20.0


def test_national_month_partial_bucket_uses_daily_baseline():
    class DS:
        def fetch_national_observed_series(self, query):
            return [
                ObservedPoint(date=dt.date(2024, 1, 1), temperature=10.0),
                ObservedPoint(date=dt.date(2024, 1, 2), temperature=14.0),
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(month=1, day_of_month=1, mean=1.0),
                DailyBaselinePoint(month=1, day_of_month=2, mean=3.0),
            ]

        def fetch_national_monthly_baseline(self):
            return [MonthlyBaselinePoint(month=1, mean=20.0)]

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(mean=999.0)

        def fetch_stations_daily_series(self, query):
            return []

    out = get_temperature_deviation(
        data_source=DS(),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        granularity="month",
        station_ids=(),
        include_national=True,
    )

    point = out["national"]["data"][0]

    assert point["baseline_mean"] == 2.0


def test_national_year_full_bucket_uses_yearly_baseline():
    class DS:
        def fetch_national_observed_series(self, query):
            return [
                ObservedPoint(
                    date=dt.date(2024, 1, 1) + dt.timedelta(days=i), temperature=10.0
                )
                for i in range(366)  # 2024 bissextile
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(
                    month=(dt.date(2024, 1, 1) + dt.timedelta(days=i)).month,
                    day_of_month=(dt.date(2024, 1, 1) + dt.timedelta(days=i)).day,
                    mean=1.0,
                )
                for i in range(366)
            ]

        def fetch_national_monthly_baseline(self):
            return []

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(mean=50.0)

        def fetch_stations_daily_series(self, query):
            return []

    out = get_temperature_deviation(
        data_source=DS(),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 12, 31),
        granularity="year",
        station_ids=(),
        include_national=True,
    )

    point = out["national"]["data"][0]

    assert point["baseline_mean"] == 50.0


def test_national_year_partial_bucket_uses_daily_baseline():
    class DS:
        def fetch_national_observed_series(self, query):
            return [
                ObservedPoint(date=dt.date(2024, 1, 1), temperature=10.0),
                ObservedPoint(date=dt.date(2024, 1, 2), temperature=14.0),
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(month=1, day_of_month=1, mean=1.0),
                DailyBaselinePoint(month=1, day_of_month=2, mean=3.0),
            ]

        def fetch_national_monthly_baseline(self):
            return []

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(mean=999.0)

        def fetch_stations_daily_series(self, query):
            return []

    out = get_temperature_deviation(
        data_source=DS(),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        granularity="year",
        station_ids=(),
        include_national=True,
    )

    point = out["national"]["data"][0]

    assert point["baseline_mean"] == 2.0


def test_temperature_deviation_graph__business_month_extends_source_window_to_full_month():
    class DS:
        def fetch_national_observed_series(self, query):
            assert query.date_start == dt.date(2024, 1, 1)
            assert query.date_end == dt.date(2024, 1, 31)

            return [
                ObservedPoint(date=dt.date(2024, 1, 1), temperature=10.0),
                ObservedPoint(date=dt.date(2024, 1, 31), temperature=14.0),
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(month=1, day_of_month=1, mean=1.0),
                DailyBaselinePoint(month=1, day_of_month=31, mean=3.0),
            ]

        def fetch_national_monthly_baseline(self):
            return [MonthlyBaselinePoint(month=1, mean=20.0)]

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(mean=999.0)

        def fetch_stations_daily_series(self, query):
            assert query.date_start == dt.date(2024, 1, 1)
            assert query.date_end == dt.date(2024, 1, 31)
            return []

    out = get_temperature_deviation(
        data_source=DS(),
        date_start=dt.date(2024, 1, 15),
        date_end=dt.date(2024, 1, 20),
        granularity="month",
        station_ids=(),
        include_national=True,
    )

    point = out["national"]["data"][0]

    # observé agrégé sur le mois complet fetché
    assert point["date"] == dt.date(2024, 1, 1)
    assert point["temperature"] == 12.0


def test_temperature_deviation_graph_business_year_extends_source_window_to_full_year():
    class DS:
        def fetch_national_observed_series(self, query):
            assert query.date_start == dt.date(2024, 1, 1)
            assert query.date_end == dt.date(2024, 12, 31)

            return [
                ObservedPoint(date=dt.date(2024, 1, 1), temperature=10.0),
                ObservedPoint(date=dt.date(2024, 12, 31), temperature=14.0),
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(month=1, day_of_month=1, mean=1.0),
                DailyBaselinePoint(month=12, day_of_month=31, mean=3.0),
            ]

        def fetch_national_monthly_baseline(self):
            return []

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(mean=50.0)

        def fetch_stations_daily_series(self, query):
            assert query.date_start == dt.date(2024, 1, 1)
            assert query.date_end == dt.date(2024, 12, 31)
            return []

    out = get_temperature_deviation(
        data_source=DS(),
        date_start=dt.date(2024, 3, 15),
        date_end=dt.date(2024, 9, 10),
        granularity="year",
        station_ids=(),
        include_national=True,
    )

    point = out["national"]["data"][0]

    assert point["date"] == dt.date(2024, 1, 1)
    assert point["temperature"] == 12.0
