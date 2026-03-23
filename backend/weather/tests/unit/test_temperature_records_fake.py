import datetime as dt

from weather.data_sources.records_fake import FakeRecordsDataSource
from weather.services.records.types import RecordsQuery


def test_fake_records_returns_requested_stations():
    ds = FakeRecordsDataSource()
    stations_ids = ("12345678", "87654321")
    query = RecordsQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 12, 31),
        station_ids=stations_ids,
        record_kind="absolute",
        record_scope="all_time",
        type_records="all",
    )

    out = ds.fetch_records(query)
    expected_station_names = [f"Station {sid}" for sid in stations_ids]
    assert len(out) == 2
    assert tuple(s.id for s in out) == stations_ids
    assert [s.name for s in out] == expected_station_names


def test_fake_records_type_records_hot_keeps_only_hot_records():
    ds = FakeRecordsDataSource()
    query = RecordsQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 12, 31),
        station_ids=("12345678",),
        record_kind="historical",
        record_scope="monthly",
        type_records="hot",
    )

    out = ds.fetch_records(query)

    assert len(out) == 1
    station = out[0]
    assert len(station.hot_records) > 0
    assert station.cold_records == ()


def test_fake_records_type_records_cold_keeps_only_cold_records():
    ds = FakeRecordsDataSource()
    query = RecordsQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 12, 31),
        station_ids=("12345678",),
        record_kind="historical",
        record_scope="monthly",
        type_records="cold",
    )

    out = ds.fetch_records(query)

    assert len(out) == 1
    station = out[0]
    assert station.hot_records == ()
    assert len(station.cold_records) > 0


def test_fake_records_absolute_returns_single_record_per_type():
    ds = FakeRecordsDataSource()
    query = RecordsQuery(
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 12, 31),
        station_ids=("12345678",),
        record_kind="absolute",
        record_scope="monthly",
        type_records="all",
    )

    out = ds.fetch_records(query)

    station = out[0]
    assert len(station.hot_records) == 1
    assert len(station.cold_records) == 1
