import datetime as dt

from weather.services.temperature_extremes.service import compute_extremes_overview
from weather.services.temperature_extremes.types import (
    ExtremesOverviewQuery,
    ExtremesOverviewResult,
    ExtremesOverviewStation,
    Pagination,
)


class DummyDataSource:
    def __init__(self):
        self.query_received = None

    def fetch_station_overview(self, query):
        self.query_received = query
        return ExtremesOverviewResult(
            pagination=Pagination(total_count=2, limit=50, offset=0),
            stations=[
                ExtremesOverviewStation(
                    station_id="07156",
                    station_name="Station A",
                    tmax_mean=25.1234,
                    tmin_mean=12.0122,
                    tmean_mean=18.5678,
                    lat=48.8,
                    lon=2.3,
                    alt=42.0,
                    department="75",
                    region="Île-de-France",
                    classe_recente=1,
                    date_de_creation=dt.date(1948, 1, 1),
                    date_de_fermeture=None,
                ),
                ExtremesOverviewStation(
                    station_id="07157",
                    station_name="Station B",
                    tmax_mean=30.9876,
                    tmin_mean=13.9012,
                    tmean_mean=22.4444,
                    lat=43.3,
                    lon=5.4,
                    alt=15.0,
                    department="13",
                    region="Provence-Alpes-Côte d'Azur",
                    classe_recente=2,
                    date_de_creation=dt.date(2000, 1, 1),
                    date_de_fermeture=dt.date(2020, 12, 31),
                ),
            ],
        )


def _default_query(**overrides) -> ExtremesOverviewQuery:
    params = {
        "date_start": dt.date(2024, 1, 1),
        "date_end": dt.date(2024, 12, 31),
    }
    params.update(overrides)
    return ExtremesOverviewQuery(**params)


def test_compute_overview_happy_path():
    ds = DummyDataSource()

    out = compute_extremes_overview(data_source=ds, query=_default_query())

    assert "pagination" in out
    assert "stations" in out
    assert len(out["stations"]) == 2


def test_compute_overview_rounds_floats_to_two_decimals():
    ds = DummyDataSource()

    out = compute_extremes_overview(data_source=ds, query=_default_query())

    s = out["stations"][0]
    assert s["tmax_mean"] == 25.12
    assert s["tmin_mean"] == 12.01
    assert s["tmean_mean"] == 18.57


def test_compute_overview_propagates_pagination():
    ds = DummyDataSource()

    out = compute_extremes_overview(data_source=ds, query=_default_query())

    p = out["pagination"]
    assert p["total_count"] == 2
    assert p["limit"] == 50
    assert p["offset"] == 0


def test_compute_overview_returns_all_station_fields():
    ds = DummyDataSource()

    out = compute_extremes_overview(data_source=ds, query=_default_query())

    s = out["stations"][0]
    assert s["station_id"] == "07156"
    assert s["station_name"] == "Station A"
    assert s["lat"] == 48.8
    assert s["lon"] == 2.3
    assert s["alt"] == 42.0
    assert s["department"] == "75"
    assert s["region"] == "Île-de-France"
    assert s["classe_recente"] == 1
    assert s["date_de_creation"] == dt.date(1948, 1, 1)
    assert s["date_de_fermeture"] is None


def test_compute_overview_passes_query_to_datasource():
    ds = DummyDataSource()

    query = _default_query(
        type="tmin",
        station_ids=("07149", "07255"),
        departments=("75",),
        tmax_min=10.0,
        ordering="station_name",
        limit=25,
        offset=50,
    )

    compute_extremes_overview(data_source=ds, query=query)

    assert ds.query_received is query
