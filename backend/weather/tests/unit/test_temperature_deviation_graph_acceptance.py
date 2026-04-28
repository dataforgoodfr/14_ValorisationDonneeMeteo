import datetime as dt

from weather.services.temperature_deviation.types import (
    DailyBaselinePoint,
    DailyDeviationPoint,
    MonthlyBaselinePoint,
    ObservedPoint,
    StationDailySeries,
    YearlyBaselinePoint,
)
from weather.services.temperature_deviation.use_case import get_temperature_deviation


class FakeTemperatureDeviationAcceptanceDataSource:
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
                        baseline_mean=8.0,
                    ),
                ],
            )
        ]


def test_temperature_deviation_acceptance_month_partial_uses_daily_baseline_for_national():
    ds = FakeTemperatureDeviationAcceptanceDataSource()

    out = get_temperature_deviation(
        data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        granularity="month",
        station_ids=("07149",),
        include_national=True,
    )

    national = out["national"]["data"]
    stations = out["stations"]

    assert len(national) == 1
    assert len(stations) == 1

    point = national[0]

    assert point["date"] == dt.date(2024, 1, 1)
    assert point["temperature"] == 12.0
    assert point["baseline_mean"] == 2.0  # (1 + 3) / 2
    assert point["deviation"] == 10

    station = stations[0]
    assert station["station_id"] == "07149"
    assert station["station_name"] == "Station 07149"
    assert len(station["data"]) == 1

    station_point = station["data"][0]
    assert station_point["date"] == dt.date(2024, 1, 1)
    assert station_point["temperature"] == 8.0
    assert station_point["baseline_mean"] == 7.0
    assert station_point["deviation"] == 1.0


def test_temperature_deviation_acceptance_year_month_of_year_slice():
    class DS:
        def fetch_national_observed_series(self, query):
            return [
                ObservedPoint(dt.date(2023, 2, 1), 10),
                ObservedPoint(dt.date(2023, 2, 2), 20),
                ObservedPoint(dt.date(2024, 2, 1), 30),
                ObservedPoint(dt.date(2024, 2, 2), 40),
            ]

        def fetch_national_daily_baseline(self):
            return []

        def fetch_national_monthly_baseline(self):
            return [MonthlyBaselinePoint(2, 5)]

        def fetch_national_yearly_baseline(self):
            return YearlyBaselinePoint(100)

        def fetch_stations_daily_series(self, query):
            return []

    ds = DS()

    out = get_temperature_deviation(
        data_source=ds,
        date_start=dt.date(2023, 1, 1),
        date_end=dt.date(2024, 12, 31),
        granularity="year",
        slice_type="month_of_year",
        month_of_year=2,
    )

    pts = out["national"]["data"]

    assert len(pts) == 2
    assert pts[0]["date"] == dt.date(2023, 2, 1)
    assert pts[1]["date"] == dt.date(2024, 2, 1)
    assert pts[0]["baseline_mean"] == 5


def test_temperature_deviation_acceptance_month_day_of_month_slice():
    class DS:
        def fetch_national_observed_series(self, query):
            return [
                ObservedPoint(dt.date(2024, 1, 31), 10),
                ObservedPoint(dt.date(2024, 2, 29), 20),
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(1, 31, 1),
                DailyBaselinePoint(2, 29, 2),
            ]

        def fetch_national_monthly_baseline(self):
            return []

        def fetch_national_yearly_baseline(self):
            return None

        def fetch_stations_daily_series(self, query):
            return []

    ds = DS()

    out = get_temperature_deviation(
        data_source=ds,
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 2, 29),
        granularity="month",
        slice_type="day_of_month",
        day_of_month=31,
    )

    pts = out["national"]["data"]

    assert len(pts) == 2
    assert pts[0]["date"] == dt.date(2024, 1, 31)
    assert pts[1]["date"] == dt.date(2024, 2, 29)


def test_temperature_deviation_acceptance_year_day_of_month_slice_clamp():
    class DS:
        def fetch_national_observed_series(self, query):
            return [
                ObservedPoint(dt.date(2020, 2, 29), 10),
                ObservedPoint(dt.date(2021, 2, 28), 20),
            ]

        def fetch_national_daily_baseline(self):
            return [
                DailyBaselinePoint(2, 29, 1),
                DailyBaselinePoint(2, 28, 2),
            ]

        def fetch_national_monthly_baseline(self):
            return []

        def fetch_national_yearly_baseline(self):
            return None

        def fetch_stations_daily_series(self, query):
            return []

    ds = DS()

    out = get_temperature_deviation(
        data_source=ds,
        date_start=dt.date(2020, 1, 1),
        date_end=dt.date(2021, 12, 31),
        granularity="year",
        slice_type="day_of_month",
        month_of_year=2,
        day_of_month=29,
    )

    pts = out["national"]["data"]

    assert pts[0]["date"] == dt.date(2020, 2, 29)
    assert pts[1]["date"] == dt.date(2021, 2, 28)
