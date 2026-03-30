import datetime as dt

from weather.services.records.types import StationRecords, TemperatureRecord
from weather.services.records.use_case import get_records


def test_temperature_records_business_returns_datasource_output():
    expected = (
        StationRecords(
            id="12345678",
            name="Station 12345678",
            hot_records=(TemperatureRecord(value=35.2, date=dt.date(2024, 1, 15)),),
            cold_records=(TemperatureRecord(value=-8.1, date=dt.date(2024, 2, 15)),),
        ),
    )

    class DeterministicRecordsDataSource:
        def fetch_records(self, query):
            return expected

    out = get_records(
        data_source=DeterministicRecordsDataSource(),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 12, 31),
        station_ids=("12345678",),
        record_kind="absolute",
        record_scope="all_time",
        type_records="all",
    )

    assert out == expected


def test_temperature_records_business_passes_departments_to_datasource():
    captured = {}

    class CapturingRecordsDataSource:
        def fetch_records(self, query):
            captured["query"] = query
            return ()

    get_records(
        data_source=CapturingRecordsDataSource(),
        date_start=dt.date(2024, 1, 1),
        date_end=dt.date(2024, 12, 31),
        station_ids=("07149", "07222"),
        departments=("07", "13"),
        record_kind="historical",
        record_scope="monthly",
        type_records="hot",
    )

    q = captured["query"]
    assert q.departments == ("07", "13")
