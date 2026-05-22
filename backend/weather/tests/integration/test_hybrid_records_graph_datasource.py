from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import HybridRecordsGraphDataSource
from weather.services.records_graph.types import RecordsGraphRequest
from weather.tests.helpers.horaire import insert_mv_quotidienne_realtime
from weather.tests.helpers.records import insert_mv_record, set_cutoff
from weather.tests.helpers.stations import insert_station


def _req(**kwargs) -> RecordsGraphRequest:
    defaults = {
        "date_start": dt.date(1990, 1, 1),
        "date_end": dt.date(2027, 12, 31),
        "granularity": "year",
        "period_type": "all_time",
        "type_records": "hot",
        "month": None,
        "season": None,
        "territoire": "france",
        "territoire_id": None,
    }
    defaults.update(kwargs)
    return RecordsGraphRequest(**defaults)


@pytest.mark.django_db
def test_new_temperature_in_realtime_pipeline_appears_as_new_record():
    """
    Scénario réaliste : un record historique existe dans mv_records_battus.
    Une nouvelle température (qui bat le record) arrive via le pipeline
    temps-réel et est propagée dans mv_quotidienne_realtime par le job de
    refresh, ce que v_quotidienne expose. Le hybride doit détecter ce
    nouveau record au prochain appel.

    En test, mv_quotidienne_realtime est une vraie table (pas une MV) :
    on simule donc directement l'état post-refresh en insérant la ligne
    agrégée qui serait produite par le job de rafraîchissement en prod.
    """
    code = "75114001"
    insert_station(code, "Station Realtime", departement=75)

    historical_date = dt.date(2003, 7, 15)
    insert_mv_record(
        station_code=code,
        station_name="Station Realtime",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=38.0,
        date=historical_date,
        department=75,
    )
    set_cutoff(dt.date(2025, 12, 31))

    ds = HybridRecordsGraphDataSource()
    request = _req()

    first = ds.fetch_graph(request)
    first_for_station = [r for r in first.records if r.station_id.strip() == code]
    assert [(r.date, r.valeur) for r in first_for_station] == [(historical_date, 38.0)]

    new_date = dt.date(2026, 7, 15)
    new_value = 45.0
    insert_mv_quotidienne_realtime(code, new_date, tn=20.0, tx=new_value)

    second = ds.fetch_graph(request)
    second_for_station = [r for r in second.records if r.station_id.strip() == code]
    values = {(r.date, r.valeur) for r in second_for_station}
    assert (historical_date, 38.0) in values
    assert (new_date, new_value) in values

    bucket_2026 = next(b for b in second.buckets if b.bucket == "2026")
    assert bucket_2026.nb_records_battus == 1
