import datetime as dt

from weather.data_sources.temperature_records_fake import (
    FakeTemperatureRecordsDataSource,
)
from weather.services.temperature_records.types import TemperatureRecordsRequest


def test_fake_records_hot_returns_non_empty_list():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    assert len(result) >= 5
    assert all(e.record_value >= 30 for e in result)


def test_fake_records_cold_returns_non_empty_list():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="cold")
    result = ds.fetch_records(req)

    assert len(result) >= 5
    assert all(e.record_value <= 0 for e in result)


def test_fake_records_month_period_type_does_not_raise():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="month", type_records="hot", month=7)
    result = ds.fetch_records(req)

    assert len(result) >= 1


def test_fake_records_season_period_type_does_not_raise():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="season", type_records="cold", season="winter"
    )
    result = ds.fetch_records(req)

    assert len(result) >= 1


def test_fake_records_all_time_period_type_does_not_raise():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    assert len(result) >= 1


def test_fake_records_entries_have_correct_shape():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    for entry in result:
        assert isinstance(entry.station_id, str)
        assert isinstance(entry.station_name, str)
        assert isinstance(entry.department, str)
        assert isinstance(entry.record_value, float)
        assert isinstance(entry.record_date, dt.date)


def test_fake_records_is_deterministic():
    ds = FakeTemperatureRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")

    r1 = ds.fetch_records(req)
    r2 = ds.fetch_records(req)

    assert r1 == r2
