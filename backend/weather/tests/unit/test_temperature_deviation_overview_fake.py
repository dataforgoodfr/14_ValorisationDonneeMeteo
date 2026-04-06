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
        page=1,
        page_size=10,
        ordering="-deviation",
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 500
    assert result.pagination.page == 1
    assert result.pagination.page_size == 10
    assert result.pagination.total_pages == 50
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
        page=1,
        page_size=10,
        ordering="-deviation",
    )
    query_page_2 = TemperatureDeviationOverviewQuery(
        date_start=dt.date(2025, 3, 1),
        date_end=dt.date(2025, 3, 31),
        page=2,
        page_size=10,
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
        page=1,
        page_size=50,
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
        page=1,
        page_size=50,
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
        page=1,
        page_size=50,
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
        page=1,
        page_size=50,
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
        page=1,
        page_size=50,
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
        page=1,
        page_size=20,
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
        page=1,
        page_size=20,
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
        page=1,
        page_size=50,
    )

    result = ds.fetch_station_overview(query)

    assert result.pagination.total_count == 0
    assert result.pagination.page == 1
    assert result.pagination.page_size == 50
    assert result.pagination.total_pages == 0
    assert result.stations == []
