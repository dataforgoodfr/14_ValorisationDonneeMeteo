import datetime as dt

from weather.services.records.types import (
    RecordsQuery,
    StationRecords,
    TemperatureRecord,
)
from weather.services.records.use_case import get_records


class ConfigurableRecordsDataSource:
    """Fake data source retournant des StationRecords préconfigurées.

    Capture la dernière requête reçue pour permettre des assertions dessus.
    """

    def __init__(self, preset: tuple[StationRecords, ...]) -> None:
        self._preset = preset
        self.last_query: RecordsQuery | None = None

    def fetch_records(self, query: RecordsQuery) -> tuple[StationRecords, ...]:
        self.last_query = query
        return self._preset


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


# ---------------------------------------------------------------------------
# Scénario B1 — Records all-time chauds : progression sur plusieurs années
# ---------------------------------------------------------------------------


def test_alltime_hot_records_progression():
    """
    GIVEN  Une station avec 3 records de chaleur progressifs et 1 non-record
    WHEN   get_records(record_scope=all_time, type_records=hot, record_kind=historical)
    THEN   Les 3 records sont retournés, le non-record est absent
    """
    hot = (
        TemperatureRecord(value=35.0, date=dt.date(1990, 7, 20)),
        TemperatureRecord(value=42.5, date=dt.date(2003, 8, 5)),
        TemperatureRecord(value=45.1, date=dt.date(2019, 6, 28)),
    )
    preset = (
        StationRecords(
            id="99001001", name="Station Canicule", hot_records=hot, cold_records=()
        ),
    )
    ds = ConfigurableRecordsDataSource(preset)

    results = get_records(
        data_source=ds,
        record_scope="all_time",
        type_records="hot",
        record_kind="historical",
    )

    assert len(results) == 1
    station = results[0]
    hot_dates = {r.date for r in station.hot_records}
    assert dt.date(1990, 7, 20) in hot_dates
    assert dt.date(2003, 8, 5) in hot_dates
    assert dt.date(2019, 6, 28) in hot_dates
    assert {r.value for r in station.hot_records} == {35.0, 42.5, 45.1}
    assert ds.last_query.record_scope == "all_time"
    assert ds.last_query.type_records == "hot"


# ---------------------------------------------------------------------------
# Scénario B2 — Records mensuels : passage du mois dans la requête
# ---------------------------------------------------------------------------


def test_monthly_hot_records_passes_scope_to_datasource():
    """
    GIVEN  Une station avec 2 records mensuels pour juillet
    WHEN   get_records(record_scope=monthly, type_records=hot)
    THEN   La requête transmise au data source contient record_scope=monthly
           Et les 2 records sont retournés
    """
    hot = (
        TemperatureRecord(value=38.0, date=dt.date(2000, 7, 15)),
        TemperatureRecord(value=41.0, date=dt.date(2022, 7, 3)),
    )
    preset = (
        StationRecords(
            id="99002001", name="Station Juillet", hot_records=hot, cold_records=()
        ),
    )
    ds = ConfigurableRecordsDataSource(preset)

    results = get_records(
        data_source=ds,
        record_scope="monthly",
        type_records="hot",
        record_kind="historical",
    )

    assert ds.last_query.record_scope == "monthly"
    hot_dates = {r.date for r in results[0].hot_records}
    assert dt.date(2000, 7, 15) in hot_dates
    assert dt.date(2022, 7, 3) in hot_dates


# ---------------------------------------------------------------------------
# Scénario B3 — Records all-time froids : deux stations, valeurs correctes
# ---------------------------------------------------------------------------


def test_alltime_cold_records_two_stations():
    """
    GIVEN  Station A avec un record froid à -22.0 °C, Station B à -18.5 °C
    WHEN   get_records(record_scope=all_time, type_records=cold)
    THEN   Station A a cold_records=(-22.0), Station B a cold_records=(-18.5)
           Les hot_records sont vides
    """
    preset = (
        StationRecords(
            id="99003001",
            name="Station Grand Froid A",
            hot_records=(),
            cold_records=(TemperatureRecord(value=-22.0, date=dt.date(1985, 1, 16)),),
        ),
        StationRecords(
            id="99003002",
            name="Station Grand Froid B",
            hot_records=(),
            cold_records=(TemperatureRecord(value=-18.5, date=dt.date(1963, 2, 11)),),
        ),
    )
    ds = ConfigurableRecordsDataSource(preset)

    results = get_records(
        data_source=ds,
        record_scope="all_time",
        type_records="cold",
        record_kind="historical",
    )

    assert len(results) == 2
    by_id = {s.id: s for s in results}
    assert by_id["99003001"].cold_records[0].value == -22.0
    assert by_id["99003001"].cold_records[0].date == dt.date(1985, 1, 16)
    assert by_id["99003001"].hot_records == ()
    assert by_id["99003002"].cold_records[0].value == -18.5
    assert ds.last_query.type_records == "cold"


# ---------------------------------------------------------------------------
# Scénario B4 — record_kind=absolute : paramètre transmis au data source
# ---------------------------------------------------------------------------


def test_absolute_kind_passes_record_kind_to_datasource():
    """
    GIVEN  Une station avec un seul record (le record absolu en vigueur)
    WHEN   get_records(record_kind=absolute)
    THEN   La requête transmise contient record_kind=absolute
           Et le seul record est bien retourné
    """
    preset = (
        StationRecords(
            id="99004001",
            name="Station Absolu",
            hot_records=(TemperatureRecord(value=44.0, date=dt.date(2019, 6, 28)),),
            cold_records=(),
        ),
    )
    ds = ConfigurableRecordsDataSource(preset)

    results = get_records(
        data_source=ds,
        record_scope="all_time",
        type_records="hot",
        record_kind="absolute",
    )

    assert ds.last_query.record_kind == "absolute"
    assert len(results[0].hot_records) == 1
    assert results[0].hot_records[0].value == 44.0
    assert results[0].hot_records[0].date == dt.date(2019, 6, 28)


# ---------------------------------------------------------------------------
# Scénario B5 — Filtre par département : transmis au data source
# ---------------------------------------------------------------------------


def test_department_filter_passed_to_datasource():
    """
    GIVEN  Deux stations (dept 13 et dept 69)
    WHEN   get_records avec departments=("13",)
    THEN   La requête transmise contient departments=("13",)
           Seule la station du dept 13 est retournée (le fake filtre via la requête)
    """
    preset_dept13 = StationRecords(
        id="99005001",
        name="Station Marseille",
        hot_records=(TemperatureRecord(value=40.0, date=dt.date(2019, 7, 28)),),
        cold_records=(),
    )
    ds = ConfigurableRecordsDataSource((preset_dept13,))

    results = get_records(
        data_source=ds,
        record_scope="all_time",
        type_records="hot",
        record_kind="historical",
        departments=("13",),
    )

    assert ds.last_query.departments == ("13",)
    assert len(results) == 1
    assert results[0].id == "99005001"
