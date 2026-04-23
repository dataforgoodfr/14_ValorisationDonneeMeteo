import datetime as dt

from weather.services.temperature_minmax.service import compute_minmax_overview
from weather.services.temperature_minmax.types import (
    MinMaxOverviewQuery,
    MinMaxOverviewResult,
    MinMaxOverviewStation,
    Pagination,
)


class DummyDataSource:
    def __init__(self):
        self.query_received = None

    def fetch_station_overview(self, query):
        self.query_received = query
        return MinMaxOverviewResult(
            pagination=Pagination(total_count=2, limit=50, offset=0),
            stations=[
                MinMaxOverviewStation(
                    station_id="07156",
                    station_name="Station A",
                    textreme_mean=25.1234,
                    tmean_mean=18.5678,
                    lat=48.8,
                    lon=2.3,
                    alt=42.0,
                    department="75",
                    region="Île-de-France",
                    classe=1,
                    annee_de_creation=1948,
                    annee_de_fermeture=None,
                ),
                MinMaxOverviewStation(
                    station_id="07157",
                    station_name="Station B",
                    textreme_mean=30.9876,
                    tmean_mean=22.4444,
                    lat=43.3,
                    lon=5.4,
                    alt=15.0,
                    department="13",
                    region="Provence-Alpes-Côte d'Azur",
                    classe=2,
                    annee_de_creation=2000,
                    annee_de_fermeture=2020,
                ),
            ],
        )


def _default_query(**overrides) -> MinMaxOverviewQuery:
    params = {
        "date_start": dt.date(2024, 1, 1),
        "date_end": dt.date(2024, 12, 31),
    }
    params.update(overrides)
    return MinMaxOverviewQuery(**params)


def test_compute_overview_happy_path():
    ds = DummyDataSource()

    out = compute_minmax_overview(data_source=ds, query=_default_query())

    assert "pagination" in out
    assert "stations" in out
    assert len(out["stations"]) == 2


def test_compute_overview_rounds_floats_to_two_decimals():
    ds = DummyDataSource()

    out = compute_minmax_overview(data_source=ds, query=_default_query())

    s = out["stations"][0]
    assert s["textreme_mean"] == 25.12
    assert s["tmean_mean"] == 18.57


def test_compute_overview_propagates_pagination():
    ds = DummyDataSource()

    out = compute_minmax_overview(data_source=ds, query=_default_query())

    p = out["pagination"]
    assert p["total_count"] == 2
    assert p["limit"] == 50
    assert p["offset"] == 0


def test_compute_overview_returns_all_station_fields():
    ds = DummyDataSource()

    out = compute_minmax_overview(data_source=ds, query=_default_query())

    s = out["stations"][0]
    assert s["station_id"] == "07156"
    assert s["station_name"] == "Station A"
    assert s["lat"] == 48.8
    assert s["lon"] == 2.3
    assert s["alt"] == 42.0
    assert s["department"] == "75"
    assert s["region"] == "Île-de-France"
    assert s["classe"] == 1
    assert s["annee_de_creation"] == 1948
    assert s["annee_de_fermeture"] is None


def test_compute_overview_passes_query_to_datasource():
    ds = DummyDataSource()

    query = _default_query(
        type="tmin",
        station_ids=("07149", "07255"),
        departments=("75",),
        textreme_min=10.0,
        ordering="station_name",
        limit=25,
        offset=50,
    )

    compute_minmax_overview(data_source=ds, query=query)

    assert ds.query_received is query
