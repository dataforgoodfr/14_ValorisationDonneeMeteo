import datetime as dt

from weather.data_sources.temperature_deviation_fake import (
    FakeTemperatureDeviationDailyDataSource,
)
from weather.services.temperature_deviation.types import (
    DailyDeviationPoint,
    StationDailySeries,
)
from weather.services.temperature_deviation.use_case import get_temperature_deviation


def test_temperature_deviation_business_day_happy_path():
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


def test_temperature_deviation_business_month_aggregates_to_one_point_per_month():
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


def test_temperature_deviation_business_without_national_returns_only_stations():
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


def test_temperature_deviation_business_deviation_equals_temperature_minus_baseline_mean():
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


def test_temperature_deviation_business_returns_expected_payload_on_simple_input():
    class DeterministicTemperatureDeviationDataSource:
        def fetch_national_daily_series(self, query):
            return [
                DailyDeviationPoint(
                    date=dt.date(2024, 1, 1),
                    temperature=10.0,
                    baseline_mean=8.0,
                ),
                DailyDeviationPoint(
                    date=dt.date(2024, 1, 2),
                    temperature=12.0,
                    baseline_mean=9.0,
                ),
            ]

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

    result = get_temperature_deviation(
        data_source=DeterministicTemperatureDeviationDataSource(),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 1, 2),
        granularity="day",
        station_ids=("07149",),
        include_national=True,
    )

    expected = {
        "national": {
            "data": [
                {
                    "date": dt.date(2024, 1, 1),
                    "deviation": 2.0,
                    "temperature": 10.0,
                    "baseline_mean": 8.0,
                },
                {
                    "date": dt.date(2024, 1, 2),
                    "deviation": 3.0,
                    "temperature": 12.0,
                    "baseline_mean": 9.0,
                },
            ]
        },
        "stations": [
            {
                "station_id": "07149",
                "station_name": "Station 07149",
                "data": [
                    {
                        "date": dt.date(2024, 1, 1),
                        "deviation": 1.0,
                        "temperature": 7.0,
                        "baseline_mean": 6.0,
                    },
                    {
                        "date": dt.date(2024, 1, 2),
                        "deviation": 0.5,
                        "temperature": 9.0,
                        "baseline_mean": 8.5,
                    },
                ],
            }
        ],
    }

    assert result == expected
