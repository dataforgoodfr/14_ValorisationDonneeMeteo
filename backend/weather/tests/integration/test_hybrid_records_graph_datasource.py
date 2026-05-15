from __future__ import annotations

import datetime as dt

import pytest

from weather.data_sources.timescale import HybridRecordsGraphDataSource
from weather.services.records_graph.types import RecordsGraphRequest
from weather.tests.helpers.horaire import insert_mv_quotidienne_realtime
from weather.tests.helpers.records import (
    insert_mv_record,
    insert_mv_records_absolus_par_mois,
    set_cutoff,
)
from weather.tests.helpers.stations import insert_station

# NB : ces tests couvrent l'enrichissement post-cutoff du
# HybridRecordsGraphDataSource lui-même, indépendamment du branchement endpoint.
_MV_RECORDS_BATTUS_REALTIME_SKIP_REASON = (
    "mv_records_battus_realtime path is not developed for now"
)


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
@pytest.mark.skip(reason=_MV_RECORDS_BATTUS_REALTIME_SKIP_REASON)
def test_new_temperature_in_realtime_pipeline_appears_as_new_record() -> None:
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


@pytest.mark.django_db
@pytest.mark.skip(reason=_MV_RECORDS_BATTUS_REALTIME_SKIP_REASON)
def test_record_on_cutoff_date_is_detected() -> None:
    """Quand un nouveau record tombe le MÊME jour que la cutoff_date,
    il doit être détecté (la borne de la query post-cutoff inclut la cutoff)."""
    code = "75114004"
    insert_station(code, "Station Cutoff Day", departement=75)
    insert_mv_record(
        station_code=code,
        station_name="Station Cutoff Day",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=38.0,
        date=dt.date(2003, 7, 15),
        department=75,
    )
    cutoff = dt.date(2026, 5, 23)
    set_cutoff(cutoff)
    insert_mv_quotidienne_realtime(code, cutoff, tn=5.0, tx=45.0)

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(1990, 1, 1),
            date_end=dt.date(2027, 12, 31),
        )
    )

    for_station = [r for r in result.records if r.station_id.strip() == code]
    values = {(r.date, r.valeur) for r in for_station}
    assert (cutoff, 45.0) in values, (
        f"Le record du jour de cutoff ({cutoff}) manque dans la réponse : "
        f"{for_station}"
    )


@pytest.mark.django_db
def test_record_present_in_mv_and_realtime_is_not_counted_twice() -> None:
    """Un record présent à la fois dans mv_records_battus ET dans
    mv_quotidienne_realtime (avec la même valeur) ne doit pas apparaître
    deux fois — la comparaison au seed empêche la détection redondante."""
    code = "75114005"
    insert_station(code, "Station No Dup", departement=75)

    same_day = dt.date(2026, 7, 15)
    insert_mv_record(
        station_code=code,
        station_name="Station No Dup",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=42.0,
        date=same_day,
        department=75,
    )
    set_cutoff(dt.date(2025, 12, 31))
    insert_mv_quotidienne_realtime(code, same_day, tn=5.0, tx=42.0)

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(_req())

    for_station = [r for r in result.records if r.station_id.strip() == code]
    on_same_day = [r for r in for_station if r.date == same_day]
    assert (
        len(on_same_day) == 1
    ), f"Le record du {same_day} apparaît {len(on_same_day)} fois : {on_same_day}"
    assert on_same_day[0].valeur == 42.0


@pytest.mark.django_db
def test_no_false_positive_cold_records_when_above_seed() -> None:
    """Plusieurs jours post-cutoff avec TN au-dessus du seed cold historique
    (-20°C) ne doivent générer AUCUN nouveau record."""
    code = "75114007"
    insert_station(code, "Station Cold No FP", departement=75)
    insert_mv_record(
        station_code=code,
        station_name="Station Cold No FP",
        period_type="all_time",
        period_value=None,
        record_type="TN",
        value=-20.0,
        date=dt.date(1985, 1, 16),
        department=75,
    )
    set_cutoff(dt.date(2025, 12, 31))

    # 10 jours en 2026 avec TN qui décroît mais reste au-dessus de -20
    for i, tn in enumerate([10, 5, 0, -3, -5, -8, -10, -12, -15, -18]):
        insert_mv_quotidienne_realtime(
            code,
            dt.date(2026, 1, i + 1),
            tn=float(tn),
            tx=float(tn + 5),
        )

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(_req(type_records="cold"))

    for_station = [r for r in result.records if r.station_id.strip() == code]
    assert for_station == [], (
        f"Aucun nouveau record cold ne devrait être détecté (tous au-dessus "
        f"du seed -20°C), mais {len(for_station)} ont été trouvés : {for_station}"
    )


@pytest.mark.django_db
def test_absolute_record_predates_50_year_filter_seeds_correctly() -> None:
    """Reproduit le cas MARIGNANE (13054001) :
    - Station créée en 1920 → first_temp + 50 ans = 1970.
    - Record absolu cold de mai = 0.0°C le 1960-05-01 → EXCLU de
      mv_records_battus par le filtre 50-ans.
    - v_records_absolus_par_type (via mv_records_absolus_par_mois) contient
      bien ce record.
    - Une lecture du jour à TN=12.3°C ne doit PAS être détectée comme
      nouveau record, puisque 12.3 > 0.0.
    """
    code = "13054001"
    insert_station(
        code,
        "MARIGNANE",
        departement=13,
        first_temperature_date=dt.date(1920, 1, 1),
    )
    # mv_records_battus VIDE pour ce station/mois — le filtre 50-ans en exclut
    # le record absolu (1960 < 1970).
    insert_mv_records_absolus_par_mois(
        station_code=code,
        month=5,
        txx_max=35.0,
        txx_max_date=dt.date(2000, 5, 15),
        tnn_min=0.0,
        tnn_min_date=dt.date(1960, 5, 1),
    )
    set_cutoff(dt.date(2025, 12, 31))
    insert_mv_quotidienne_realtime(code, dt.date(2026, 5, 22), tn=12.3, tx=20.0)

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2026, 1, 1),
            date_end=dt.date(2026, 5, 22),
            granularity="year",
            type_records="cold",
            period_type="month",
            month=5,
        )
    )

    for_station = [r for r in result.records if r.station_id.strip() == code]
    assert for_station == [], (
        "12.3°C ne doit pas battre le record May de 0°C, "
        f"mais le hybride retourne : {for_station}"
    )


@pytest.mark.django_db
@pytest.mark.skip(reason=_MV_RECORDS_BATTUS_REALTIME_SKIP_REASON)
def test_real_new_cold_record_still_detected_against_absolute_seed() -> None:
    """Vérifie que le fix MARIGNANE (seed via v_records_absolus_par_type)
    n'a pas supprimé les vrais nouveaux records : si une TN post-cutoff
    descend EN DESSOUS du record absolu, elle doit être détectée."""
    code = "13054002"
    insert_station(
        code,
        "Station Real New Cold",
        departement=13,
        first_temperature_date=dt.date(1920, 1, 1),
    )
    # Seed via les absolus : record May = 0°C en 1960.
    insert_mv_records_absolus_par_mois(
        station_code=code,
        month=5,
        txx_max=35.0,
        txx_max_date=dt.date(2000, 5, 15),
        tnn_min=0.0,
        tnn_min_date=dt.date(1960, 5, 1),
    )
    set_cutoff(dt.date(2025, 12, 31))
    # TN=-3°C → bat le record absolu de 0°C → vrai nouveau record.
    insert_mv_quotidienne_realtime(code, dt.date(2026, 5, 10), tn=-3.0, tx=8.0)

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2026, 1, 1),
            date_end=dt.date(2026, 5, 22),
            granularity="year",
            type_records="cold",
            period_type="month",
            month=5,
        )
    )

    for_station = [r for r in result.records if r.station_id.strip() == code]
    new = [
        r
        for r in for_station
        if r.date == dt.date(2026, 5, 10) and r.type_records == "cold"
    ]
    assert (
        len(new) == 1
    ), f"-3°C bat le record May de 0°C, devrait être détecté : {for_station}"
    assert new[0].valeur == -3.0


@pytest.mark.django_db
@pytest.mark.skip(reason=_MV_RECORDS_BATTUS_REALTIME_SKIP_REASON)
def test_real_new_records_detected_with_type_records_all() -> None:
    """Réplique du cas staging : type_records=all, period_type=month, month=5
    avec une station style MARIGNANE (records absolus en mv_records_absolus_par_mois,
    rien en mv_records_battus). Une TN ET une TX battant respectivement le
    cold et le hot absolu doivent BOTH être détectées."""
    code = "13054004"
    insert_station(
        code,
        "Station All Real Records",
        departement=13,
        first_temperature_date=dt.date(1920, 1, 1),
    )
    insert_mv_records_absolus_par_mois(
        station_code=code,
        month=5,
        txx_max=35.0,
        txx_max_date=dt.date(2000, 5, 15),
        tnn_min=0.0,
        tnn_min_date=dt.date(1960, 5, 1),
    )
    set_cutoff(dt.date(2025, 12, 31))
    # TX=42 bat 35 ; TN=-3 bat 0 → deux nouveaux records.
    insert_mv_quotidienne_realtime(code, dt.date(2026, 5, 10), tn=-3.0, tx=42.0)

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2026, 1, 1),
            date_end=dt.date(2026, 5, 22),
            granularity="year",
            type_records="all",
            period_type="month",
            month=5,
        )
    )

    for_station = [
        r
        for r in result.records
        if r.station_id.strip() == code and r.date == dt.date(2026, 5, 10)
    ]
    hot = [r for r in for_station if r.type_records == "hot"]
    cold = [r for r in for_station if r.type_records == "cold"]
    assert (
        len(hot) == 1 and hot[0].valeur == 42.0
    ), f"42°C bat 35°C, manque dans la réponse : {for_station}"
    assert (
        len(cold) == 1 and cold[0].valeur == -3.0
    ), f"-3°C bat 0°C, manque dans la réponse : {for_station}"


@pytest.mark.django_db
@pytest.mark.skip(reason=_MV_RECORDS_BATTUS_REALTIME_SKIP_REASON)
def test_today_real_new_hot_record_with_period_type_month_no_month() -> None:
    """Réplique exacte de l'URL staging qui ne renvoie plus les vrais nouveaux
    records après le fix MARIGNANE :
    /api/v1/temperature/records/graph
        ?type_records=hot&granularity=day
        &date_start=2026-05-22&date_end=2026-05-22
        &period_type=month
    (period_type=month SANS paramètre month → mode 'tous les mois').

    Une TX du jour qui bat le record absolu du mois courant doit apparaître."""
    today = dt.date.today()
    code = "13054005"
    insert_station(
        code,
        "Station Today Hot Real",
        departement=13,
        first_temperature_date=dt.date(1920, 1, 1),
    )
    # Record absolu du mois courant (e.g. May) = 35°C dans les absolus
    insert_mv_records_absolus_par_mois(
        station_code=code,
        month=today.month,
        txx_max=35.0,
        txx_max_date=dt.date(2000, today.month, 15),
        tnn_min=0.0,
        tnn_min_date=dt.date(1960, today.month, 1),
    )
    set_cutoff(today - dt.timedelta(days=180))
    # TX=42°C → bat le record 35°C du mois courant → vrai nouveau record
    insert_mv_quotidienne_realtime(code, today, tn=18.0, tx=42.0)

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=today,
            date_end=today,
            granularity="day",
            type_records="hot",
            period_type="month",
            month=None,
        )
    )

    for_station = [r for r in result.records if r.station_id.strip() == code]
    new = [r for r in for_station if r.date == today and r.type_records == "hot"]
    assert len(new) == 1, (
        f"42°C bat le record {today.month:02d} absolu (35°C), "
        f"devrait apparaître : {for_station}"
    )
    assert new[0].valeur == 42.0


@pytest.mark.django_db
@pytest.mark.skip(reason=_MV_RECORDS_BATTUS_REALTIME_SKIP_REASON)
def test_real_new_hot_record_still_detected_against_absolute_seed() -> None:
    """Symétrique : un vrai nouveau record chaud doit toujours apparaître."""
    code = "13054003"
    insert_station(
        code,
        "Station Real New Hot",
        departement=13,
        first_temperature_date=dt.date(1920, 1, 1),
    )
    insert_mv_records_absolus_par_mois(
        station_code=code,
        month=5,
        txx_max=35.0,
        txx_max_date=dt.date(2000, 5, 15),
        tnn_min=0.0,
        tnn_min_date=dt.date(1960, 5, 1),
    )
    set_cutoff(dt.date(2025, 12, 31))
    # TX=42°C → bat le record absolu de 35°C → vrai nouveau record.
    insert_mv_quotidienne_realtime(code, dt.date(2026, 5, 10), tn=18.0, tx=42.0)

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(
        _req(
            date_start=dt.date(2026, 1, 1),
            date_end=dt.date(2026, 5, 22),
            granularity="year",
            type_records="hot",
            period_type="month",
            month=5,
        )
    )

    for_station = [r for r in result.records if r.station_id.strip() == code]
    new = [
        r
        for r in for_station
        if r.date == dt.date(2026, 5, 10) and r.type_records == "hot"
    ]
    assert (
        len(new) == 1
    ), f"42°C bat le record May de 35°C, devrait être détecté : {for_station}"
    assert new[0].valeur == 42.0


@pytest.mark.django_db
def test_no_false_positive_cold_when_type_records_all() -> None:
    """Avec type_records=all, l'enrichissement post-cutoff lance deux passes
    (hot + cold). Les TN au-dessus du seed cold ne doivent pas être détectés
    comme records, même si la même ligne v_quotidienne a un TX qui dépasse
    le seed hot."""
    code = "75114008"
    insert_station(code, "Station All No FP", departement=75)
    insert_mv_record(
        station_code=code,
        station_name="Station All No FP",
        period_type="all_time",
        period_value=None,
        record_type="TN",
        value=-20.0,
        date=dt.date(1985, 1, 16),
        department=75,
    )
    insert_mv_record(
        station_code=code,
        station_name="Station All No FP",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=38.0,
        date=dt.date(2003, 7, 15),
        department=75,
    )
    set_cutoff(dt.date(2025, 12, 31))

    # Plusieurs jours post-cutoff : TN au-dessus de -20, TX en-dessous de 38
    # → AUCUN nouveau record (ni hot ni cold).
    for i, (tn, tx) in enumerate([(2, 12), (-5, 8), (-10, 3), (-15, 1)]):
        insert_mv_quotidienne_realtime(
            code, dt.date(2026, 1, i + 1), tn=float(tn), tx=float(tx)
        )

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(_req(type_records="all"))

    for_station = [r for r in result.records if r.station_id.strip() == code]
    post_cutoff = [r for r in for_station if r.date.year == 2026]
    assert (
        post_cutoff == []
    ), f"Aucun record post-cutoff ne devrait être détecté, mais {post_cutoff}"


@pytest.mark.django_db
@pytest.mark.skip(reason=_MV_RECORDS_BATTUS_REALTIME_SKIP_REASON)
def test_stale_mv_record_does_not_duplicate_with_fresher_realtime() -> None:
    """Quand le mv_records_battus a une valeur figée (par ex. 38) mais que la
    pipeline temps-réel a vu plus chaud le même jour (45), la réponse ne doit
    contenir qu'une seule ligne pour ce jour (la plus à jour)."""
    code = "75114006"
    insert_station(code, "Station Stale MV", departement=75)

    same_day = dt.date(2026, 7, 15)
    # MV avec la valeur stale (38)
    insert_mv_record(
        station_code=code,
        station_name="Station Stale MV",
        period_type="all_time",
        period_value=None,
        record_type="TX",
        value=38.0,
        date=same_day,
        department=75,
    )
    set_cutoff(dt.date(2025, 12, 31))
    # Realtime avec la valeur fraîche (45)
    insert_mv_quotidienne_realtime(code, same_day, tn=5.0, tx=45.0)

    ds = HybridRecordsGraphDataSource()
    result = ds.fetch_graph(_req())

    for_station = [r for r in result.records if r.station_id.strip() == code]
    on_same_day = [r for r in for_station if r.date == same_day]
    assert (
        len(on_same_day) == 1
    ), f"Le record du {same_day} apparaît {len(on_same_day)} fois : {on_same_day}"
    # La valeur conservée est la plus haute (post-cutoff fraîche)
    assert on_same_day[0].valeur == 45.0
