from __future__ import annotations

import datetime as dt

import pytest
from django.db import connection

from weather.data_sources.timescale import (
    TimescaleTemperatureAbsoluteRecordsDataSource,
)
from weather.services.temperature_records.types import TemperatureRecordsRequest
from weather.tests.helpers.stations import insert_station


def insert_mv_records_absolus_par_mois(
    *,
    station_code: str,
    month: int,
    txx_max: float,
    txx_max_date: str,
    tnn_min: float,
    tnn_min_date: str,
) -> None:
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO public.mv_records_absolus_par_mois
                (station_code,     month,     txx_max,     txx_max_date,     tnn_min,     tnn_min_date)
            VALUES
                (%(station_code)s, %(month)s, %(txx_max)s, %(txx_max_date)s, %(tnn_min)s, %(tnn_min_date)s)
            """,
            {
                "station_code": station_code,
                "month": month,
                "txx_max": txx_max,
                "txx_max_date": txx_max_date,
                "tnn_min": tnn_min,
                "tnn_min_date": tnn_min_date,
            },
        )


# =========================
# Happy paths : period_type=all_time
# =========================


@pytest.mark.django_db
def test_fetch_records_hot_all_time_returns_max_across_all_months():
    """
    GIVEN  Une station avec un record d'avril (25°C) et un de juillet (42°C)
    WHEN   period_type=all_time, type_records=hot
    THEN   Seul le record max all-time (juillet, 42°C) est retourné
    """
    station_code = "76200001"
    insert_station(
        station_code,
        "Station All Time Hot",
        departement=76,
        lat=49.0,
        lon=1.0,
        alt=50.0,
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=4,
        txx_max=25.0,
        txx_max_date="2018-04-20",
        tnn_min=-5.0,
        tnn_min_date="1985-04-15",
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-25",
        tnn_min=10.0,
        tnn_min_date="2000-07-01",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    entries = [e for e in result.entries if e.station_id == station_code]
    assert len(entries) == 1
    entry = entries[0]
    assert entry.record_value == 42.0
    assert entry.record_date == dt.date(2019, 7, 25)
    assert entry.station_name == "Station All Time Hot"
    assert entry.department == "76"
    assert entry.lat == 49.0
    assert entry.lon == 1.0
    assert entry.alt == 50.0


@pytest.mark.django_db
def test_fetch_records_cold_all_time_returns_min_across_all_months():
    """
    GIVEN  Une station avec un record cold de janvier (-25°C) et un de novembre (-5°C)
    WHEN   period_type=all_time, type_records=cold
    THEN   Seul le record min all-time (janvier, -25°C) est retourné
    """
    station_code = "76200002"
    insert_station(station_code, "Station All Time Cold", departement=76)
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=1,
        txx_max=10.0,
        txx_max_date="2000-01-15",
        tnn_min=-25.0,
        tnn_min_date="1985-01-16",
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=11,
        txx_max=18.0,
        txx_max_date="2010-11-15",
        tnn_min=-5.0,
        tnn_min_date="2010-11-20",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="cold")
    result = ds.fetch_records(req)

    entries = [e for e in result.entries if e.station_id == station_code]
    assert len(entries) == 1
    assert entries[0].record_value == -25.0
    assert entries[0].record_date == dt.date(1985, 1, 16)


# =========================
# period_type=month
# =========================


@pytest.mark.django_db
def test_fetch_records_month_filters_by_specific_month():
    """
    GIVEN  Une station avec un record en juillet (42°C) et un en août (38°C)
    WHEN   period_type=month, month=7
    THEN   Seul le record de juillet est retourné
    """
    station_code = "76200003"
    insert_station(station_code, "Station Month Filter", departement=76)
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-25",
        tnn_min=-5.0,
        tnn_min_date="2000-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=8,
        txx_max=38.0,
        txx_max_date="2020-08-15",
        tnn_min=-3.0,
        tnn_min_date="2005-08-10",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="month", type_records="hot", month=7)
    result = ds.fetch_records(req)

    entries = [e for e in result.entries if e.station_id == station_code]
    assert len(entries) == 1
    assert entries[0].record_value == 42.0
    assert entries[0].record_date == dt.date(2019, 7, 25)


# =========================
# period_type=season
# =========================


@pytest.mark.django_db
def test_fetch_records_season_winter_aggregates_across_dec_jan_feb():
    """
    GIVEN  Records hot en décembre (10°C), janvier (12°C), février (15°C)
    WHEN   period_type=season, season=winter, type_records=hot
    THEN   Seule la valeur max hivernale (février, 15°C) est retournée
    """
    station_code = "76200004"
    insert_station(station_code, "Station Winter Hot", departement=76)
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=12,
        txx_max=10.0,
        txx_max_date="2018-12-20",
        tnn_min=-5.0,
        tnn_min_date="1990-12-10",
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=1,
        txx_max=12.0,
        txx_max_date="2019-01-20",
        tnn_min=-8.0,
        tnn_min_date="1985-01-15",
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=2,
        txx_max=15.0,
        txx_max_date="2019-02-25",
        tnn_min=-3.0,
        tnn_min_date="2000-02-10",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="season", type_records="hot", season="winter"
    )
    result = ds.fetch_records(req)

    entries = [e for e in result.entries if e.station_id == station_code]
    assert len(entries) == 1
    assert entries[0].record_value == 15.0
    assert entries[0].record_date == dt.date(2019, 2, 25)


@pytest.mark.django_db
def test_fetch_records_season_summer_excludes_other_seasons():
    """
    GIVEN  Un record d'été (juillet, 42°C) et un d'hiver (janvier, 12°C)
    WHEN   period_type=season, season=summer
    THEN   Seul le record d'été est retourné
    """
    station_code = "76200005"
    insert_station(station_code, "Station Summer", departement=76)
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-25",
        tnn_min=-5.0,
        tnn_min_date="2000-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=1,
        txx_max=12.0,
        txx_max_date="2019-01-20",
        tnn_min=-8.0,
        tnn_min_date="1985-01-15",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="season", type_records="hot", season="summer"
    )
    result = ds.fetch_records(req)

    entries = [e for e in result.entries if e.station_id == station_code]
    assert len(entries) == 1
    assert entries[0].record_value == 42.0
    assert entries[0].record_date == dt.date(2019, 7, 25)


# =========================
# Filtres territoire
# =========================


@pytest.mark.django_db
def test_fetch_records_territoire_department_filters_other_departments():
    """
    GIVEN  Une station en Seine-Maritime (76) et une à Paris (75)
    WHEN   territoire=department, territoire_id=76
    THEN   Seule la station du 76 est retournée
    """
    s_76 = "76200010"
    s_75 = "75200010"
    insert_station(s_76, "Station 76", departement=76)
    insert_station(s_75, "Station 75", departement=75)
    insert_mv_records_absolus_par_mois(
        station_code=s_76,
        month=7,
        txx_max=40.0,
        txx_max_date="2019-07-15",
        tnn_min=-10.0,
        tnn_min_date="1985-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code=s_75,
        month=7,
        txx_max=41.0,
        txx_max_date="2019-07-15",
        tnn_min=-12.0,
        tnn_min_date="1985-07-01",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        territoire="department",
        territoire_id="76",
    )
    result = ds.fetch_records(req)

    station_ids = {e.station_id for e in result.entries}
    assert s_76 in station_ids
    assert s_75 not in station_ids


@pytest.mark.django_db
def test_fetch_records_territoire_station_returns_only_one_station():
    """
    GIVEN  Deux stations dans le même département
    WHEN   territoire=station, territoire_id=<une station>
    THEN   Seule la station ciblée est retournée
    """
    s1 = "76200011"
    s2 = "76200012"
    insert_station(s1, "Station Cible", departement=76)
    insert_station(s2, "Station Voisine", departement=76)
    insert_mv_records_absolus_par_mois(
        station_code=s1,
        month=7,
        txx_max=40.0,
        txx_max_date="2019-07-15",
        tnn_min=-10.0,
        tnn_min_date="1985-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code=s2,
        month=7,
        txx_max=41.0,
        txx_max_date="2019-07-15",
        tnn_min=-12.0,
        tnn_min_date="1985-07-01",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        territoire="station",
        territoire_id=s1,
    )
    result = ds.fetch_records(req)

    station_ids = {e.station_id for e in result.entries}
    assert s1 in station_ids
    assert s2 not in station_ids


# =========================
# Filtres de date
# =========================


@pytest.mark.django_db
def test_fetch_records_date_range_excludes_records_outside_window():
    """
    GIVEN  Une station avec un record en 2019 et un en 1985
    WHEN   date_start=2010-01-01, date_end=2020-12-31
    THEN   Seul le record dans la fenêtre est retourné
    """
    station_code = "76200020"
    insert_station(station_code, "Station Date Filter", departement=76)
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-25",
        tnn_min=-5.0,
        tnn_min_date="2000-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=8,
        txx_max=38.0,
        txx_max_date="1985-08-15",
        tnn_min=-3.0,
        tnn_min_date="2005-08-10",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="month",
        type_records="hot",
        month=8,
        date_start=dt.date(2010, 1, 1),
        date_end=dt.date(2020, 12, 31),
    )
    result = ds.fetch_records(req)

    entries = [e for e in result.entries if e.station_id == station_code]
    assert entries == []


# =========================
# Filtres classe_recente
# =========================


@pytest.mark.django_db
def test_fetch_records_classe_recente_max_excludes_higher_classes():
    """
    GIVEN  Une station classe 1 et une station classe 3
    WHEN   classe_recente_min=1, classe_recente_max=2
    THEN   Seule la station classe 1 est retournée
    """
    s_c1 = "76200030"
    s_c3 = "76200031"
    insert_station(s_c1, "Station Classe 1", departement=76, classe_recente=1)
    insert_station(s_c3, "Station Classe 3", departement=76, classe_recente=3)
    insert_mv_records_absolus_par_mois(
        station_code=s_c1,
        month=7,
        txx_max=40.0,
        txx_max_date="2019-07-15",
        tnn_min=-10.0,
        tnn_min_date="1985-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code=s_c3,
        month=7,
        txx_max=41.0,
        txx_max_date="2019-07-15",
        tnn_min=-12.0,
        tnn_min_date="1985-07-01",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        classe_recente_min=1,
        classe_recente_max=2,
    )
    result = ds.fetch_records(req)

    station_ids = {e.station_id for e in result.entries}
    assert s_c1 in station_ids
    assert s_c3 not in station_ids


# =========================
# Pagination
# =========================


@pytest.mark.django_db
def test_fetch_records_pagination_page_and_page_size():
    """
    GIVEN  Trois stations chacune avec un record
    WHEN   page=2, page_size=1, sort=-record_value
    THEN   Une entrée retournée, total_count=3, page=2
    """
    codes = ["76200040", "76200041", "76200042"]
    for i, code in enumerate(codes):
        insert_station(code, f"Station Pagination {i}", departement=76)
        insert_mv_records_absolus_par_mois(
            station_code=code,
            month=7,
            txx_max=40.0 + i,
            txx_max_date=f"201{i}-07-15",
            tnn_min=-10.0 - i,
            tnn_min_date=f"198{i}-07-01",
        )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        territoire="department",
        territoire_id="76",
        page=2,
        page_size=1,
        sort="-record_value",
    )
    result = ds.fetch_records(req)

    assert result.pagination.total_count == 3
    assert result.pagination.page == 2
    assert result.pagination.page_size == 1
    assert result.pagination.total_pages == 3
    assert len(result.entries) == 1
    # Avec sort=-record_value : page 1 = 42°C, page 2 = 41°C, page 3 = 40°C
    assert result.entries[0].record_value == 41.0


# =========================
# Sorting
# =========================


@pytest.mark.django_db
def test_fetch_records_sorting_by_value_desc():
    """
    GIVEN  Deux stations avec des valeurs différentes (38°C et 45°C)
    WHEN   sort=-record_value
    THEN   Le record le plus chaud est retourné en premier
    """
    s1 = "76200050"
    s2 = "76200051"
    insert_station(s1, "Station Hot", departement=76)
    insert_station(s2, "Station Hotter", departement=76)
    insert_mv_records_absolus_par_mois(
        station_code=s1,
        month=7,
        txx_max=38.0,
        txx_max_date="2019-07-15",
        tnn_min=-10.0,
        tnn_min_date="1985-07-01",
    )
    insert_mv_records_absolus_par_mois(
        station_code=s2,
        month=7,
        txx_max=45.0,
        txx_max_date="2019-07-15",
        tnn_min=-12.0,
        tnn_min_date="1985-07-01",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(
        period_type="all_time",
        type_records="hot",
        territoire="department",
        territoire_id="76",
        sort="-record_value",
    )
    result = ds.fetch_records(req)

    entries = [e for e in result.entries if e.station_id in {s1, s2}]
    assert len(entries) == 2
    assert entries[0].record_value == 45.0
    assert entries[1].record_value == 38.0


# =========================
# Types
# =========================


@pytest.mark.django_db
def test_fetch_records_returns_correct_entry_types():
    """Valide les types des champs de TemperatureRecordEntry."""
    station_code = "76200060"
    insert_station(
        station_code,
        "Station Types",
        departement=76,
        lat=49.5,
        lon=1.5,
        alt=120.0,
        annee_de_creation=1960,
    )
    insert_mv_records_absolus_par_mois(
        station_code=station_code,
        month=7,
        txx_max=42.0,
        txx_max_date="2019-07-25",
        tnn_min=-15.0,
        tnn_min_date="1985-01-16",
    )

    ds = TimescaleTemperatureAbsoluteRecordsDataSource()
    req = TemperatureRecordsRequest(period_type="all_time", type_records="hot")
    result = ds.fetch_records(req)

    entries = [e for e in result.entries if e.station_id == station_code]
    assert len(entries) == 1
    entry = entries[0]
    assert isinstance(entry.station_id, str)
    assert isinstance(entry.station_name, str)
    assert isinstance(entry.department, str)
    assert isinstance(entry.record_value, float)
    assert isinstance(entry.record_date, dt.date)
    assert isinstance(entry.lat, float)
    assert isinstance(entry.lon, float)
    assert isinstance(entry.alt, float)
    assert isinstance(entry.classe_recente, int)
    assert isinstance(entry.date_de_creation, dt.date)
