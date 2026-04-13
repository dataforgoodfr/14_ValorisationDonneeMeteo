import datetime as dt

from weather.data_sources.temperature_deviation_fake import (
    FakeTemperatureDeviationOverviewDataSource,
)
from weather.services.temperature_deviation.types import (
    TemperatureDeviationOverviewQuery,
)


def test_fake_overview_national_mean_deviation_is_stable():
    ds = FakeTemperatureDeviationOverviewDataSource()

    out = ds.fetch_national_mean_deviation(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
    )

    assert out == 1.5


def test_fake_overview_returns_first_page_with_default_ordering():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        offset=0,
        limit=10,
        ordering="-deviation",
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 500
    assert result.pagination.offset == 0
    assert result.pagination.limit == 10
    assert len(result.stations) == 10

    assert result.stations[0].deviation >= result.stations[1].deviation

    station = result.stations[0]

    assert station.lat is not None
    assert station.lon is not None
    assert station.department is not None
    assert station.alt is not None
    assert station.region is not None


def test_fake_overview_pagination_returns_second_page():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query_page_1 = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        offset=0,
        limit=10,
        ordering="-deviation",
    )
    query_page_2 = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        offset=10,
        limit=10,
        ordering="-deviation",
    )

    result_page_1 = ds.fetch_station_overview(query_page_1)
    result_page_2 = ds.fetch_station_overview(query_page_2)

    assert len(result_page_1.stations) == 10
    assert len(result_page_2.stations) == 10
    assert result_page_1.stations != result_page_2.stations


def test_fake_overview_station_search_filters_results():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        station_search="70010",
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count > 0
    assert all("70010" in s.station_name for s in result.stations)


def test_fake_overview_temperature_mean_min_filters_results():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        temperature_mean_min=25.0,
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count > 0
    assert all(s.temperature_mean >= 25.0 for s in result.stations)


def test_fake_overview_temperature_mean_max_filters_results():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        temperature_mean_max=12.0,
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count > 0
    assert all(s.temperature_mean <= 12.0 for s in result.stations)


def test_fake_overview_deviation_min_filters_results():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        deviation_min=2.0,
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count > 0
    assert all(s.deviation >= 2.0 for s in result.stations)


def test_fake_overview_deviation_max_filters_results():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        deviation_max=0.0,
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count > 0
    assert all(s.deviation <= 0.0 for s in result.stations)


def test_fake_overview_ordering_by_deviation_ascending():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        ordering="deviation",
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert len(result.stations) >= 2
    assert result.stations[0].deviation <= result.stations[1].deviation


def test_fake_overview_ordering_by_station_name_ascending():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        ordering="station_name",
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert len(result.stations) >= 2
    assert result.stations[0].station_name <= result.stations[1].station_name


def test_fake_overview_returns_empty_page_when_filters_match_nothing():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        deviation_min=999.0,
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.offset == 0
    assert result.pagination.limit == 50
    assert result.stations == []


def test_fake_overview_offset_changes_returned_slice():
    ds = FakeTemperatureDeviationOverviewDataSource()

    result_1 = ds.fetch_station_overview(
        TemperatureDeviationOverviewQuery(
            date_start=dt.date(2025, 3, 1),
            date_end=dt.date(2025, 3, 31),
            ordering="-deviation",
            offset=0,
            limit=10,
        )
    )
    result_2 = ds.fetch_station_overview(
        TemperatureDeviationOverviewQuery(
            date_start=dt.date(2025, 3, 1),
            date_end=dt.date(2025, 3, 31),
            ordering="-deviation",
            offset=10,
            limit=10,
        )
    )

    assert len(result_1.stations) == 10
    assert len(result_2.stations) == 10
    assert result_1.stations != result_2.stations


def test_fake_overview_station_ids_filters_results():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        station_ids=("70000", "70001"),
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 2
    assert len(result.stations) == 2
    assert {s.station_id for s in result.stations} == {"70000", "70001"}


def test_fake_overview_station_ids_and_station_search_are_combined():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        station_ids=("70010", "70011"),
        station_search="70010",
        offset=0,
        limit=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 1
    assert len(result.stations) == 1
    assert result.stations[0].station_id == "70010"


def test_fake_overview_ordering_by_department_ascending():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        ordering="department",
        offset=0,
        limit=20,
    )

    result = ds.fetch_station_overview(query)

    assert len(result.stations) >= 2
    assert result.stations[0].department <= result.stations[1].department


def test_fake_overview_ordering_by_region_ascending():
    ds = FakeTemperatureDeviationOverviewDataSource()

    query = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        ordering="region",
        offset=0,
        limit=20,
    )

    result = ds.fetch_station_overview(query)

    assert len(result.stations) >= 2
    assert result.stations[0].region <= result.stations[1].region
