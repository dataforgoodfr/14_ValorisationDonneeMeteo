import datetime as dt

from weather.services.temperature_deviation.service import (
    compute_temperature_deviation_overview,
)
from weather.services.temperature_deviation.types import (
    Pagination,
    TemperatureDeviationOverviewResult,
    TemperatureDeviationOverviewStation,
)


class DummyDataSource:
    def __init__(self):
        self.national_called_with = None
        self.query_received = None

    def fetch_national_mean_deviation(self, *, date_start, date_end):
        self.national_called_with = (date_start, date_end)
        return 1.23456

    def fetch_station_overview(self, query):
        self.query_received = query

        return TemperatureDeviationOverviewResult(
            national_deviation_mean=999.0,  # ignoré volontairement
            pagination=Pagination(
                total_count=2,
                limit=50,
                offset=0,
            ),
            stations=[
                TemperatureDeviationOverviewStation(
                    station_id="07156",
                    station_name="Station A",
                    lat=48.8,
                    lon=2.3,
                    department="75",
                    alt=42.0,
                    region="Île-de-France",
                    temperature_mean=10.1234,
                    baseline_mean=8.9876,
                    deviation=1.1358,
                ),
                TemperatureDeviationOverviewStation(
                    station_id="07157",
                    station_name="Station B",
                    lat=43.3,
                    lon=5.4,
                    department="13",
                    alt=15.0,
                    region="Provence-Alpes-Côte d'Azur",
                    temperature_mean=20.5678,
                    baseline_mean=19.1234,
                    deviation=1.4444,
                ),
            ],
        )


def test_compute_overview_happy_path():
    ds = DummyDataSource()

    out = compute_temperature_deviation_overview(
        data_source=ds,
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
    )

    assert "national" in out
    assert "pagination" in out
    assert "stations" in out

    assert out["national"]["deviation_mean"] == 1.23

    assert out["pagination"]["total_count"] == 2
    assert len(out["stations"]) == 2


def test_compute_overview_rounding():
    ds = DummyDataSource()

    out = compute_temperature_deviation_overview(
        data_source=ds,
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
    )

    s = out["stations"][0]

    assert s["temperature_mean"] == round(10.1234, 2)
    assert s["baseline_mean"] == round(8.9876, 2)
    assert s["deviation"] == round(1.1358, 2)


def test_compute_overview_propagates_pagination():
    ds = DummyDataSource()

    out = compute_temperature_deviation_overview(
        data_source=ds,
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
    )

    p = out["pagination"]

    assert p["total_count"] == 2
    assert p["limit"] == 50
    assert p["offset"] == 0


def test_compute_overview_calls_datasource_with_correct_dates():
    ds = DummyDataSource()

    compute_temperature_deviation_overview(
        data_source=ds,
        date_start=dt.date(2025, 1, 1),
        date_end=dt.date(2025, 1, 31),
    )

    assert ds.national_called_with == (
        dt.date(2025, 1, 1),
        dt.date(2025, 1, 31),
    )


def test_compute_overview_passes_query_parameters():
    ds = DummyDataSource()

    compute_temperature_deviation_overview(
        data_source=ds,
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        station_ids=("07149", "07255"),
        station_search="foo",
        temperature_mean_min=10,
        temperature_mean_max=20,
        deviation_min=1,
        deviation_max=5,
        ordering="station_name",
        offset=50,
        limit=25,
    )

    q = ds.query_received

    assert q.station_search == "foo"
    assert q.temperature_mean_min == 10
    assert q.temperature_mean_max == 20
    assert q.deviation_min == 1
    assert q.deviation_max == 5
    assert q.ordering == "station_name"
    assert q.offset == 50
    assert q.limit == 25
    assert q.station_ids == ("07149", "07255")


def test_compute_overview_national_independent_from_station_result():
    ds = DummyDataSource()

    out = compute_temperature_deviation_overview(
        data_source=ds,
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
    )

    # on vérifie qu'on utilise bien la valeur de fetch_national_mean_deviation
    assert out["national"]["deviation_mean"] == 1.23


def test_compute_overview_propagates_added_station_fields():
    ds = DummyDataSource()

    out = compute_temperature_deviation_overview(
        data_source=ds,
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
    )

    s = out["stations"][0]

    assert s["lat"] == 48.8
    assert s["lon"] == 2.3
    assert s["department"] == "75"
    assert s["alt"] == 42.0
    assert s["region"] == "Île-de-France"


def test_compute_overview_passes_added_query_parameters():
    ds = DummyDataSource()

    compute_temperature_deviation_overview(
        data_source=ds,
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        alt_min=100,
        alt_max=500,
        departments=("13", "75"),
        regions=("Occitanie",),
    )

    q = ds.query_received

    assert q.alt_min == 100
    assert q.alt_max == 500
    assert q.departments == ("13", "75")
    assert q.regions == ("Occitanie",)
